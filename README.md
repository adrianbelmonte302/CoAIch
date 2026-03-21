# CoAIch Training Lab

## Overview
This repository contains the test project for CoAIch’s twin-platform training manager. The goal is to deliver a responsive web experience and a native Android companion that both help instructors and trainees plan, run, and review AI-powered training sessions.

## Goals
- Validate the end-to-end flow of creating courses, scheduling sessions, and logging attendance from a browser.
- Deliver an Android interface for trainees to check schedules, follow guided content, and record metrics while on the move.
- Surface AI recommendations (e.g., adaptive lesson ordering, feedback summaries, auto-tagged highlights) across both platforms.

## Capabilities
- **Web control center** for administrators (course builder, calendar, analytics dashboards).
- **Android trainee app** with offline caching, progress tracking, and intelligent nudges.
- **AI assistant** that analyzes performance data and suggests next steps or follow-up resources.
- **Shared backend** that syncs user profiles, session history, and AI insights between platforms.

## Suggested Stack
Below is a starting point for each surface, but feel free to swap in alternate technologies as long as they meet the goals above:

- **Web:** React (or Next.js) + TypeScript frontend; Node.js/Express (or Nest) backend; REST/GraphQL API.
- **Android:** Kotlin with Jetpack Compose; WorkManager for syncing and Retrofit for API calls.
- **AI:** OpenAI or other LLM services for natural language insights; domain-specific models hosted on your chosen inference platform.
- **Data:** PostgreSQL (or Firebase) for structured data; optional vector store for embeddings.

## Getting Started
1. Clone the repository and create the necessary environment files (`.env`) for both web and Android modules.
2. Boot the backend API and ensure it can talk to the AI inference service you plan to use.
3. Run the web app (`npm run dev` or equivalent) while pointing it at the local API.
4. Launch the Android app via Android Studio or `gradlew installDebug`, targeting a device/emulator that can reach the backend.
5. Experiment with creating a course, marking trainees, and viewing AI-generated summaries to confirm the sync works.

## Next Steps
1. Wire up authentication (SSO, OAuth, or similar) for both frontends.
2. Build sample AI prompts and integrate them into training workflows.
3. Set up automated tests (unit, integration, UI) covering treatment of AI output.

## Contribution Notes
Feedback is welcome via issues or pull requests. Please document any additional services you add (e.g., data stores or third-party AI providers) in this README.

## License
Choose a license that matches your organization’s needs (MIT, Apache 2.0, etc.) and add it once decided.
