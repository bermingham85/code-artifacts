# Source transcript — Claude + Codex = better than either alone

- Source URL: https://www.youtube.com/watch?v=Fu5KIG2Jm1g
- Author: Mark (link via Drip campaign 2026)
- Captured: 2026-05-03
- Capture method: provided in chat by Michael (no re-transcription needed)
- Status: VERIFIED VERBATIM (raw human-pasted transcript with timestamps)

---

## Sections (as titled in source)

- 0:00  What the Codex plugin actually looks like in Claude Code
- 1:13  The $20 ChatGPT plan is enough
- 1:29  Where each model wins and where each one loses
- 2:15  Why this plugin enriches Claude Code instead of replacing it
- 2:39  Install once, switch models on the fly
- 2:56  Codex as adviser vs Codex as executor
- 3:14  The 4 real decisions hiding inside the 7 slash commands
- 3:31  Pattern 1. Everyday code review
- 3:42  Pattern 2. The adversarial planning loop
- 4:16  Pattern 3. Background rescue with the Codex SWAT team
- 4:40  The review gate. Powerful and expensive
- 5:25  Background flag and model selection in the terminal
- 6:42  Real demo. A Bitly clone audited end to end
- 7:36  Watching the rescue run while we keep building
- 8:18  The 25 minute audit Codex returned
- 8:50  The adversarial planning loop in action
- 9:23  Adding expiry dates the right way
- 10:21 Why I now spend 30 to 90 minutes purely planning
- 10:42 Pattern 3 in flow state. Build with Claude, audit with Codex in parallel
- 11:46 Pattern 4. The Debbie Downer that stops you from shipping bugs
- 12:47 Pattern 5. The full feature cycle
- 13:23 The actual economics. $100 Claude Max + $20 Codex
- 14:14 Grab the diagrams as a cheat sheet

---

## Verbatim transcript

(Provided by Michael 2026-05-03; preserved without edits other than line wrapping for readability.)

```
Every single week, somebody seems to pick a winner. One week it's Claude Code and then the next it's Codex. And this cycle keeps repeating over and over again. But while everyone wants to pick a side, the actual play is to use both. Each model has its strengths and its weaknesses. And a few weeks ago, OpenAI shipped a plugin that lets you create a dynamic duo of Claude and Codex. Barely anyone is telling you how you can use this plug-in to get the best experience possible using Claude code with the intelligence and the prowess of Codex. So, if you watch this video till the end, even if you find Claude Code feeling dumber sometimes, you'll be surprised how smart it can be when it has a sidekick that looks over its plans every single time.

Let's jump in. So, if you're less familiar with what this plugin looks like, when you go into Claude Code after installing it, which is actually very easy, all you have to do is /codex. Then, behind the scenes, you can see you have all of these options, but all of them are basically designed to look over the shoulder of Claude Code. And the way you'd install it is you just go to this URL right here and you can see it's a native plugin from OpenAI themselves. If you scroll to the very bottom, you'll see all the instructions you need to get started. And if you're feeling extra lazy, you can literally feed this URL to Claude Code and have it take the onus of installing this on your OS.

Now, obviously, the prerequisite to using this is having a ChatGPT account, but you can use the $20 plan. You don't need to overspend on the 100 or the $200 plan, especially given the way that we're going to use it. You don't need to spend that many tokens to get the full juice out of the codex models.

Now, big picture, if you go on X or on YouTube, there's always a flavor of the month or the quarter when it comes to a specific model. Nine times out of 10, we have Claude Code on one side and then Codex on the other. And then we have Gemini here sitting in the corner eating crayons where once in a while they'll release something useful, but the models for something like code are still not that great. But the bottom line here is I still think Claude Code is the best model for things like copywriting, design thinking, even design in general sometimes, as well as writing certain types of coding patterns. And when it comes to Codex, it is a master surgeon. If you tell it to do 1 2 3 4 5, it will execute that perfectly nine times out of 10. So Codex is more token efficient, especially if you have targeted changes that you want to make. So instead of digging your heels into one set of models, you can use the best of both worlds and have a devil's advocate at your side at all times.

And just to clarify, this Codex plugin isn't meant to replace Claude Code. It's very similar to having this Chrome browser right here. And up here we have a series of Chrome extensions. These extensions basically enrich our existing experience. So once in a while if you find Claude Code shoddy on creating plans one day versus the next, then having Codex review that plan iteratively leads to much better outcomes.

So once you install the Codex command line interface and log in you'll never need to log in again. And the best part is you can remotely change what model you're using. It could be 5.5x high, 5.4. You can play around with the models and see which one is the best for your use case.

And probably my favorite part is because you still have the firepower of Codex in that back and forth terminal. You can always say, you know what, I want Codex to plan and actually write this code because it seems like you're way more dialed in on this specific area than Claude Code. So it doesn't just have to be an adviser. It can also be an executor.

Now when you install the plugin, you get seven slash commands out of the box, but behind the scenes, it really boils down to four key decisions. So your four decisions would be:

1) I want Codex to look at my code, purely review it and not edit it. Just basically double check and see what flaws there are. So this is meant to be polite and not steerable. And when I say steerable means you can't do /codex:review and then tell it to do something very specific or focus on one specific bug that you've adjusted.

2) Now let's say you're going back and forth with Claude Code and then eventually you want to add one specific feature, but you're not really sure if the plan makes sense. This is where it makes sense to use this command which is my favorite one which is called /codex:adversarial-review and this is really the glorified devil's advocate where you can tell it: listen, I want you to review this exact plan that Claude Code just came up with for this specific feature. So you can actually pinpoint accuracy, tell it what to look at, and it will even ask you: do you want me to look at a brand new thread and explore a brand new thread using Codex or do you want me to use the pre-existing threads that you've used Codex for in the past.

3) Now the next slash command is aptly named codex rescue and the whole point of it is bringing in the equivalent of Codex SWAT team members to take a look at all of your existing code in Claude Code. So instead of doing something very pinpoint, you are looking at a more holistic overview of your entire codebase. So let's say you vibe coded something with Opus 4.7 and you keep hitting walls no matter what you try. Bringing in the Codex army to take a look at it and audit all the blind spots that Claude Code might have in its coding patterns might be the kickstart that you need to get unstuck.

4) This last one is a very powerful but also very expensive slash command to run. And this is basically telling Codex, I want you to automatically no matter what, every single time Claude Code generates code, I want you to double check it. Which in theory again sounds amazing, but when it comes to actual tokenomics, if you don't have the $100, $200 ChatGPT plan and you're using a more potent model like 5.5, you will struggle to pay both bills at the same time. This one might make sense if you're working on something in production that's extremely sensitive and you want to double and triple check every single step for whatever changes you're making.

Now, using this in the terminal, you want to pay attention to one small detail. If you do /codex and any one of these, let's do the adversarial review. So you can tell it things like --background. So you can run this review in the background while you go back and forth with your typical Claude Code session and you can do things like giving it specific scope just using these dash commands. But if you use something more heavy duty like codex rescue and we do codex rescue and we do space, you'll see you have different parameters many of which are the same as the first. But in this case you can also manipulate which model you use from Codex what it should solve. So this is where you can write in plain English, go and rescue, take a look at my repo and tell me all the flaws, right? So you could send this over and you could do a --background after this and then it would run it behind the scenes and you wouldn't see it until it was completed.

[Real demo: Bitly clone — URL shortener with click tracking, etc. Codex rescue creates a session ID, runs in background. Status via /codex:status; result via /codex:result. Audit ran for ~25 minutes and surfaced critical correctness issues, scaling/perf risks, security/privacy issues, project hygiene, and items it didn't have time to verify. Cloud Code overlooks edge cases until pointed out.]

I actually have a looping function on my computer where I do slash and then some command and then it runs through and creates a plan with Claude Code, then audits the plan with Codex, and it keeps going until Codex no longer has any glaring issues to bring up. But you don't have to go that far. You could just start off with a plan v1 and then you have Codex review said plan. Then we have plan v2. And if you really want to double check whether Claude Code synthesized all of the criticisms from Codex, you can go back to Codex until Codex has nothing else to say, then you can feel a lot more confident moving forward.

So let's say you wanted to add a brand new feature to your URL shortening app and you want to add some form of expiration date for these links. So let's say "add expiry dates, don't code, go over the edge cases, time zones, and what if expiry is in the past? Output a numbered plan." So Claude Code itself will create this full plan and then if you read it, a lot of people will just close their eyes and say "yep go build it." It will say it's done and then you will check and find all the bugs for yourself. But what you can do is send this specific prompt where you do /codex:adversarial-review double check this plan against the code in [insert path here]. Then it will ask you do you want me to run this in the background or do you want to wait for the results and basically block anything else from moving forward until we have the second review.

So I'm at the point now in my agentic workflow journey where I will spend anywhere between 30 minutes to an hour and a half purely planning, not writing a single line of code. Because if you have the perfect plan or something close directionally to perfect, implementation is the easy part. It's really the planning and looking for those extra edge cases which will save you tons of time and tokens.

Now, pattern number three is useful if you're locked in and you're in a flow state because what you can do is you can keep going back and forth with Claude Code and building on your app incrementally while you have Codex go and run tests on every single feature that you make. So pattern 3 is meant to keep you in your flow state if you're going back and forth with Claude Code and you don't want to go down a rabbit hole fixing one particular bug. So essentially the workflow would be you would do /codex:rescue or /codex:adversarial-review for that specific feature, then you would wait, do /codex:status to see how it's going, or you can just do /codex:result and like you saw before you'll have the full breakdown of what happened.

Pattern number four is before you finally ship something, whether that's a PowerPoint deck or it could be an Excel file or an actual app. Cloud models are notorious for being trigger happy for shipping things. So you can put the brakes on purpose with something like a Codex to be the Debbie Downer that you really need to take a look at all of your code to see do you have anything that would expose personal data. So you can purposely employ a Debbie Downer at all times to stop your app from shipping and double triple checking that your initial requirements are set. And you'll find that Codex is good at thinking of the next second order and third order derivative consequences of not having something in there.

And pattern number five is really bringing everything together which I use every single day. Step one, I will open up and fire Claude Code, come up with a plan, go back and forth on that plan. Once we're good to go, I will then set an adversarial review on said plan to come up with adjustments to that plan. And again, I have my own slash command that loops through this entire process until we get to the part where we're ready to implement. And then when it comes to implementation, if you find Claude Code not doing the best of jobs on one particular domain, you can always ask Codex to take over the keyboard metaphorically and write the code itself. And once you're good to go, you're ready to ship.

Now, in terms of economics, assuming that you want Claude Code to still be your daily driver, I would recommend the $100 max plan from Claude Code and then you layer on the $20 from Codex because for all intents and purposes, at least the way that I'm using it, it is the plan auditor. It is the code auditor. Once in a blue moon, it will write the code itself. But because we're using it primarily for auditing, we don't need as much firepower to generate the code as you do with something like Claude Code.
```
