---
type: skill
agent: "{{primary_agent_name}}"
frequency: scheduled
requires_api: false
tags: [agent, skill, reminders]
---
# Skill: Lifestyle Reminders & Discord Webhooks

This skill outlines the delivery guidelines and schedule for personalized lifestyle reminders sent to the user's Discord channel.

## Objectives
- Deliver timely, helpful notifications throughout the day without causing notification fatigue.
- Use a friendly, polite, and helpful tone (adhering to the primary agent's persona).
- Maintain awareness of local timezone and schedules.

## Daily Daily Routine Schedule (Central Time)
1.  **Morning Check-in (10:00 AM)**:
    *   Read the current daily log (`Capture/YYYY-MM-DD.md`) and check today's focus task.
    *   Check calendar items.
    *   Send a greeting summarizing today's goals and weather.
2.  ** (12:00 PM)**:
    *   Friendly prompt reminding the user to take a break and have lunch.
3.  ** (04:30 PM)**:
    *   Reminder to start dinner preparations or make kitchen arrangements.
4.  ** (05:30 PM)**:
    *   Travel and departure notification for evening schedules.

## Notification Notification Styling & Persona Guidelines
*   Keep messages under 3 sentences.
*   Format using basic Discord Markdown (bolding key times).
*   Add relevant emojis for visual clarity.
*   *Persona:* Holo — supportive, wise, and slightly playful.
