# X32 Recorder Frontend

Modern Vue.js 3 frontend for the X32 Recorder API.

## Features

- Start/Stop recordings
- Select audio devices
- List and manage recordings
- Mobile-friendly responsive design
- Clean, modern UI

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Configuration

By default, the frontend expects the API to be running at `http://localhost:8000/api/`.
You can modify the API URL in `src/services/apiService.js`.
