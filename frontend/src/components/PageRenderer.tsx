import React from 'react';
import type { Page, Provider, Mood, KnowItem, AccentTheme } from '../lib/constants';
import KnowledgePage from './KnowledgePage';
import MemoryPage from './MemoryPage';
import AgentsPage from './AgentsPage';
import GeneratePage from './GeneratePage';
import SettingsPage from './SettingsPage';
import MonitorPanel from './MonitorPanel';
import MCPPage from './MCPPage';
import ArchitecturePage from './ArchitecturePage';

interface PageRendererProps {
  page: Page;
  prov: Provider;
  setProv: (v: Provider) => void;
  model: string;
  setModel: (v: string) => void;
  mood: Mood;
  setMood: (v: Mood) => void;
  temp: number;
  setTemp: (v: number) => void;
  sysPr: string;
  setSysPr: (v: string) => void;
  snd: boolean;
  setSnd: (v: boolean) => void;
  bright: number;
  setBright: (v: number) => void;
  fsize: number;
  setFsize: (v: number) => void;
  apiKey: string;
  setApiKey: (v: string) => void;
  orApiKey: string;
  setOrApiKey: (v: string) => void;
  groqApiKey: string;
  setGroqApiKey: (v: string) => void;
  openaiApiKey: string;
  setOpenaiApiKey: (v: string) => void;
  geminiApiKey: string;
  setGeminiApiKey: (v: string) => void;
  mimoApiKey: string;
  setMimoApiKey: (v: string) => void;
  oModels: { value: string; label: string }[];
  orModels: { value: string; label: string }[];
  customM: string;
  setCustomM: (v: string) => void;
  showCust: boolean;
  setShowCust: (v: boolean) => void;
  voicePreset:
    | 'google-female'
    | 'francisca'
    | 'maria'
    | 'google-male'
    | 'antonio'
    | 'daniel'
    | 'jarvis-cinematic'
    | 'edge-francisca'
    | 'edge-thalita';
  setVoicePreset: (
    v:
      | 'google-female'
      | 'francisca'
      | 'maria'
      | 'google-male'
      | 'antonio'
      | 'daniel'
      | 'jarvis-cinematic'
      | 'edge-francisca'
      | 'edge-thalita',
  ) => void;
  jarvisRate: number;
  setJarvisRate: (v: number) => void;
  voicePitch: number;
  setVoicePitch: (v: number) => void;
  ollSt: { running: boolean; models: string[] } | undefined;
  knows: KnowItem[];
  setKnows: (v: React.SetStateAction<KnowItem[]>) => void;
  expRoot: string;
  accentTheme: AccentTheme;
  setAccentTheme: (v: AccentTheme) => void;
  gpuEnabled: boolean;
  setGpuEnabled: (v: boolean) => void;
  checklistSteps?: { label: string; status: string; error?: string }[];
  loading?: boolean;
  thinking?: string;
  thinkOn?: boolean;
  thinkOpen?: boolean;
  setThinkOpen?: (v: boolean) => void;
  toolLogs?: { tool: string; status: string; params?: any; result?: any }[];
}

export default function PageRenderer(props: PageRendererProps) {
  const { page } = props;
  if (page === 'knowledge') return <KnowledgePage knows={props.knows} setKnows={props.setKnows} />;
  if (page === 'memory') return <MemoryPage />;
  if (page === 'agents') return <AgentsPage />;
  if (page === 'generate')
    return (
      <GeneratePage
        prov={props.prov}
        model={props.model}
        apiKey={props.apiKey}
        orApiKey={props.orApiKey}
      />
    );
  if (page === 'monitor') return <MonitorPanel />;
  if (page === 'mcp') return <MCPPage />;
  if (page === 'architecture') return <ArchitecturePage />;
  if (page === 'settings') {
    return (
      <SettingsPage
        prov={props.prov}
        setProv={props.setProv}
        model={props.model}
        setModel={props.setModel}
        mood={props.mood}
        setMood={props.setMood}
        temp={props.temp}
        setTemp={props.setTemp}
        sysPr={props.sysPr}
        setSysPr={props.setSysPr}
        snd={props.snd}
        setSnd={props.setSnd}
        bright={props.bright}
        setBright={props.setBright}
        fsize={props.fsize}
        setFsize={props.setFsize}
        voicePreset={props.voicePreset}
        setVoicePreset={props.setVoicePreset}
        jarvisRate={props.jarvisRate}
        setJarvisRate={props.setJarvisRate}
        voicePitch={props.voicePitch}
        setVoicePitch={props.setVoicePitch}
        apiKey={props.apiKey}
        setApiKey={props.setApiKey}
        orApiKey={props.orApiKey}
        setOrApiKey={props.setOrApiKey}
        groqApiKey={props.groqApiKey}
        setGroqApiKey={props.setGroqApiKey}
        openaiApiKey={props.openaiApiKey}
        setOpenaiApiKey={props.setOpenaiApiKey}
        geminiApiKey={props.geminiApiKey}
        setGeminiApiKey={props.setGeminiApiKey}
        mimoApiKey={props.mimoApiKey}
        setMimoApiKey={props.setMimoApiKey}
        oModels={props.oModels}
        orModels={props.orModels}
        customM={props.customM}
        setCustomM={props.setCustomM}
        showCust={props.showCust}
        setShowCust={props.setShowCust}
        ollSt={props.ollSt}
        accentTheme={props.accentTheme}
        setAccentTheme={props.setAccentTheme}
        gpuEnabled={props.gpuEnabled}
        setGpuEnabled={props.setGpuEnabled}
      />
    );
  }
  return null;
}
