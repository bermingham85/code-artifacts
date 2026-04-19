#!/usr/bin/env npx ts-node
/**
 * SHEGOO-BCK-CFG-00001 — Stripe Product & Price Setup
 *
 * Creates Shegoo Standard and Pro products with monthly/annual prices.
 * Checks for existing products by metadata before creating.
 * Creates two webhooks for onboarding and offboarding.
 * Saves price IDs to price-ids.json and inserts into Supabase config.
 *
 * Requires: STRIPE_SECRET_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
 */

import Stripe from 'stripe';

const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY;
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const N8N_BASE = 'http://192.168.50.246:5678';

if (!STRIPE_SECRET_KEY) throw new Error('STRIPE_SECRET_KEY not set');
if (!SUPABASE_URL) throw new Error('SUPABASE_URL not set');
if (!SUPABASE_SERVICE_ROLE_KEY) throw new Error('SUPABASE_SERVICE_ROLE_KEY not set');

const stripe = new Stripe(STRIPE_SECRET_KEY);

interface PriceIds {
  stripe_price_standard_monthly: string;
  stripe_price_standard_annual: string;
  stripe_price_pro_monthly: string;
  stripe_price_pro_annual: string;
  stripe_wh_checkout_id: string;
  stripe_wh_offboard_id: string;
}

async function findOrCreateProduct(
  name: string,
  plan: string
): Promise<string> {
  // Search existing products by metadata
  const existing = await stripe.products.search({
    query: `metadata['plan']:'${plan}' AND metadata['product']:'shegoo'`,
  });
  if (existing.data.length > 0) {
    console.log(`Found existing product: ${name} (${existing.data[0].id})`);
    return existing.data[0].id;
  }
  const product = await stripe.products.create({
    name,
    metadata: { plan, product: 'shegoo' },
  });
  console.log(`Created product: ${name} (${product.id})`);
  return product.id;
}

async function findOrCreatePrice(
  productId: string,
  unitAmount: number,
  interval: 'month' | 'year',
  nickname: string
): Promise<string> {
  // Check existing prices on the product
  const prices = await stripe.prices.list({ product: productId, active: true });
  for (const p of prices.data) {
    if (
      p.unit_amount === unitAmount &&
      p.recurring?.interval === interval &&
      p.currency === 'eur'
    ) {
      console.log(`Found existing price: ${nickname} (${p.id})`);
      return p.id;
    }
  }
  const price = await stripe.prices.create({
    product: productId,
    unit_amount: unitAmount,
    currency: 'eur',
    recurring: { interval },
    nickname,
  });
  console.log(`Created price: ${nickname} (${price.id})`);
  return price.id;
}

async function findOrCreateWebhook(
  url: string,
  events: string[],
  description: string
): Promise<{ id: string; secret: string }> {
  const endpoints = await stripe.webhookEndpoints.list({ limit: 100 });
  for (const ep of endpoints.data) {
    if (ep.url === url) {
      console.log(`Found existing webhook: ${description} (${ep.id})`);
      // Cannot retrieve secret for existing webhook
      return { id: ep.id, secret: '(existing — check Stripe dashboard)' };
    }
  }
  const endpoint = await stripe.webhookEndpoints.create({
    url,
    enabled_events: events as Stripe.WebhookEndpointCreateParams.EnabledEvent[],
    description,
  });
  console.log(`Created webhook: ${description} (${endpoint.id})`);
  return { id: endpoint.id, secret: endpoint.secret || '' };
}

async function insertConfigToSupabase(key: string, value: string) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/config`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      apikey: SUPABASE_SERVICE_ROLE_KEY!,
      Authorization: `Bearer ${SUPABASE_SERVICE_ROLE_KEY}`,
      Prefer: 'resolution=merge-duplicates',
    },
    body: JSON.stringify({
      key,
      value,
      last_verified: new Date().toISOString(),
      verified_by: 'stripe_setup',
      source_url: 'Stripe API',
      confidence: 'confirmed',
    }),
  });
  if (!res.ok) {
    console.error(`Failed to insert config ${key}: ${res.status}`);
  }
}

async function main() {
  console.log('=== Shegoo Stripe Setup ===\n');

  // Products
  const standardId = await findOrCreateProduct('Shegoo Standard', 'standard');
  const proId = await findOrCreateProduct('Shegoo Pro', 'pro');

  // Prices (amounts in cents)
  const stdMonthly = await findOrCreatePrice(standardId, 200, 'month', 'standard_monthly');
  const stdAnnual = await findOrCreatePrice(standardId, 2000, 'year', 'standard_annual');
  const proMonthly = await findOrCreatePrice(proId, 1000, 'month', 'pro_monthly');
  const proAnnual = await findOrCreatePrice(proId, 7500, 'year', 'pro_annual');

  // Webhooks
  const whCheckout = await findOrCreateWebhook(
    `${N8N_BASE}/webhook/shegoo-checkout`,
    ['checkout.session.completed'],
    'Shegoo onboarding — checkout complete'
  );
  const whOffboard = await findOrCreateWebhook(
    `${N8N_BASE}/webhook/shegoo-offboard`,
    ['customer.subscription.deleted'],
    'Shegoo offboarding — subscription cancelled'
  );

  const result: PriceIds = {
    stripe_price_standard_monthly: stdMonthly,
    stripe_price_standard_annual: stdAnnual,
    stripe_price_pro_monthly: proMonthly,
    stripe_price_pro_annual: proAnnual,
    stripe_wh_checkout_id: whCheckout.id,
    stripe_wh_offboard_id: whOffboard.id,
  };

  // Write price-ids.json
  const fs = await import('fs');
  fs.writeFileSync(
    new URL('./price-ids.json', import.meta.url).pathname.slice(1),
    JSON.stringify(result, null, 2)
  );
  console.log('\nWrote price-ids.json');

  // Insert into Supabase config
  for (const [key, value] of Object.entries(result)) {
    await insertConfigToSupabase(key, value);
  }
  if (whCheckout.secret && whCheckout.secret !== '(existing — check Stripe dashboard)') {
    await insertConfigToSupabase('stripe_wh_checkout_secret', whCheckout.secret);
  }
  if (whOffboard.secret && whOffboard.secret !== '(existing — check Stripe dashboard)') {
    await insertConfigToSupabase('stripe_wh_offboard_secret', whOffboard.secret);
  }

  console.log('\nInserted config values into Supabase');
  console.log('\n=== Setup Complete ===');
  console.log(JSON.stringify(result, null, 2));
}

main().catch(console.error);
