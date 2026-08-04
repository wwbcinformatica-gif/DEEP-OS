# Enhancement: ChatGPT-Style Voice Mode for DEEP-AUREA

## Goal
Create a polished, immersive voice conversation experience similar to ChatGPT's Advanced Voice Mode, with real-time audio visualization, smooth transitions, and interrupt capability.

## Current State
The project already has:
- Speech-to-Text (STT) via Web Speech API
- Text-to-Speech (TTS) via Edge TTS and browser SpeechSynthesis
- Auto-send voice mode
- Multiple voice presets
- Anti-echo mechanism

## Tasks

### Phase 1: Voice Mode Component
- [ ] Create `VoiceMode.tsx` - Full-screen immersive voice interface
  - Large animated orb/circle that reacts to audio levels
  - Real-time waveform visualization
  - Status indicators (listening, thinking, speaking)
  - Close button to return to normal chat
  - Verify: Component renders with placeholder UI

### Phase 2: Audio Visualization Hook
- [ ] Create `useAudioAnalyzer.ts` - Web Audio API integration
  - Connect to microphone stream
  - Analyze frequency data in real-time
  - Return audio levels for visualization
  - Cleanup on unmount
  - Verify: Hook returns live audio data

### Phase 3: Voice Mode Integration
- [ ] Add Voice Mode button to ChatPanel
  - Toggle between normal chat and voice mode
  - Pass all necessary props to VoiceMode
  - Verify: Button appears and opens voice mode

### Phase 4: Enhanced Conversation Flow
- [ ] Improve VAD (Voice Activity Detection)
  - Better silence detection
  - Smoother transitions between speaking/listening
  - Configurable sensitivity
  - Verify: Natural conversation pauses

### Phase 5: Interrupt Capability
- [ ] Add interrupt mechanism
  - User can tap/click to interrupt AI speech
  - Visual feedback when interrupted
  - Resume listening after interrupt
  - Verify: Can interrupt mid-sentence

### Phase 6: Visual Polish
- [ ] Add animations and transitions
  - Smooth orb pulsing based on audio
  - Color changes for different states
  - Particle effects (optional)
  - Verify: Fluid 60fps animations

## Done When
- [ ] Voice Mode opens with full-screen interface
- [ ] Real-time audio visualization works
- [ ] Smooth conversation flow (listen → think → speak)
- [ ] Can interrupt AI mid-speech
- [ ] Returns to normal chat seamlessly

## Notes
- Use Web Audio API for real-time analysis
- Keep existing voice presets working
- Ensure mobile compatibility
- Test with Edge TTS backend
