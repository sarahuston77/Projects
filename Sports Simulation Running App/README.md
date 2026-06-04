# Sports Simulation Running App

Native Android application (Java) that simulates and tracks running workouts. Originally developed for CSE 476 (Mobile Application Development) and extended afterwards. Backed by Firebase for authentication and real-time data sync across devices.

## Features
- Email/password authentication via Firebase Auth.
- Live exercise map view with location permissions handled through `PermissionUtils`.
- Exercise log fragment that persists workout history.
- Profile view backed by Firebase Realtime Database.
- Tabbed navigation built on `BaseActivity` with reusable fragments (`Home`, `ExerciseMap`, `ExerciseLog`, `Profile`).

## Tech stack
Android SDK · Java · Gradle (Kotlin DSL) · Firebase Auth · Firebase Realtime Database · Google Play Services Location.

## Layout
```
Sports Simulation Running App/
├── app/
│   ├── build.gradle.kts
│   └── src/main/
│       ├── AndroidManifest.xml
│       ├── java/com/example/cse476app/
│       │   ├── BaseActivity.java          # Tab host + nav scaffolding
│       │   ├── LoginActivity.java         # Firebase Auth flow
│       │   ├── HomeFragment.java
│       │   ├── ExerciseMapFragment.java   # Live run tracking
│       │   ├── ExerciseLogFragment.java   # Workout history
│       │   ├── ProfileFragment.java
│       │   └── PermissionUtils.java
│       └── res/                           # layouts, drawables, values
├── build.gradle.kts
└── settings.gradle.kts
```

## Build

```bash
./gradlew assembleDebug
```

Drop your own `google-services.json` into `app/` to wire up Firebase before building.

## Notes
This is the original course-project codebase; the repository folder is named for portability rather than the internal Gradle module name (`cse476 app`).
