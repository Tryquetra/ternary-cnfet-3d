import React from 'react';
import {
  AbsoluteFill,
  Audio,
  OffthreadVideo,
  Series,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

export interface SceneSpec {
  id: string;
  title: string;
  badge: string;
  badgeColor: string;
  formula: string;
  narration: string;
  durationInFrames: number;
}

export const SCENES: SceneSpec[] = [
  {
    id: 'scene_01_anatomy',
    title: '1. Gate-All-Around CNFET Architecture',
    badge: 'ANATOMY',
    badgeColor: '#38bdf8',
    formula: 'Si / SiO2 Substrate  |  Pd/Au Contacts  |  HfO2 High-k (IOR 1.90)',
    narration:
      'In a Carbon Nanotube Field-Effect Transistor, semiconducting single-walled carbon nanotubes bridge Palladium and Gold source and drain contacts over a silicon dioxide substrate. A coaxial Gate-All-Around stack of hafnium oxide and metal surrounds each nanotube channel.',
    durationInFrames: 526,
  },
  {
    id: 'scene_02_chirality',
    title: '2. Chiral Diameter & Threshold Voltage Modulation',
    badge: 'MANIM PLOT',
    badgeColor: '#a855f7',
    formula: 'd_CNT = 0.0783 * n (nm)   |   Eg = 0.84 eV / d_CNT   |   Vth = 0.43 V / d_CNT',
    narration:
      'The threshold voltage is inversely proportional to the nanotube diameter. The front wide (13,0) nanotube measures 1.02 nm across, yielding a low threshold of 0.42 V. The rear narrow (7,0) nanotube measures 0.55 nm, producing a high threshold of 0.78 V.',
    durationInFrames: 712,
  },
  {
    id: 'scene_03_state_minus1',
    title: '3. Balanced Ternary State -1 (Vgs < 0.42 V)',
    badge: 'TRIT -1',
    badgeColor: '#f43f5e',
    formula: 'STATE -1:  Vgs < Vth1 < Vth2   |   CH1 (13,0): OFF   |   CH2 (7,0): OFF',
    narration:
      'In balanced ternary state -1, the gate voltage remains below 0.42 V. Both conduction band barriers, Ec1 and Ec2, stay elevated, blocking electron injection into both channels.',
    durationInFrames: 471,
  },
  {
    id: 'scene_04_state_0',
    title: '4. Balanced Ternary State 0 (0.42 V <= Vgs < 0.78 V)',
    badge: 'TRIT 0',
    badgeColor: '#00f2d4',
    formula: 'STATE 0:  Vth1 <= Vgs < Vth2   |   CH1 (13,0): BALLISTIC ON   |   CH2 (7,0): OFF',
    narration:
      'In balanced ternary state 0, the gate voltage reaches the intermediate window between 0.42 V and 0.78 V. The cyan barrier Ec1 drops, triggering ballistic electron transport through the wide nanotube, while the high pink barrier Ec2 keeps the narrow nanotube switched off.',
    durationInFrames: 621,
  },
  {
    id: 'scene_05_state_plus1',
    title: '5. Balanced Ternary State +1 (Vgs >= 0.78 V)',
    badge: 'TRIT +1',
    badgeColor: '#22c55e',
    formula: 'STATE +1:  Vgs >= Vth2 > Vth1   |   CH1 (13,0): ON   |   CH2 (7,0): BALLISTIC ON',
    narration:
      'In balanced ternary state +1, the gate voltage exceeds 0.78 V. Both potential barriers drop below the source Fermi level, enabling simultaneous ballistic conduction across both carbon nanotubes.',
    durationInFrames: 456,
  },
];

const SceneSlide: React.FC<{scene: SceneSpec}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = spring({
    frame,
    fps,
    config: {damping: 18, stiffness: 120},
  });

  const fadeOut = interpolate(
    frame,
    [scene.durationInFrames - 15, scene.durationInFrames],
    [1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  const opacity = Math.min(enter, fadeOut);
  const translateY = interpolate(enter, [0, 1], [24, 0]);
  const progress = interpolate(frame, [0, scene.durationInFrames], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: '#080c14'}}>
      <OffthreadVideo
        src={staticFile(`media/${scene.id}.mp4`)}
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
      <Audio src={staticFile(`media/${scene.id}.mp3`)} />

      {/* Lower-Third Scientific HUD Overlay */}
      <div
        style={{
          position: 'absolute',
          bottom: 12,
          left: 48,
          right: 48,
          opacity,
          transform: `translateY(${translateY}px)`,
          background: 'rgba(8, 14, 26, 0.88)',
          border: `1.5px solid ${scene.badgeColor}66`,
          borderRadius: 12,
          padding: '10px 20px',
          boxShadow: '0 10px 28px rgba(0, 0, 0, 0.65)',
          fontFamily: 'Inter, system-ui, sans-serif',
          color: '#f8fafc',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 4,
          }}
        >
          <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
            <span
              style={{
                backgroundColor: scene.badgeColor,
                color: '#040810',
                fontWeight: 800,
                fontSize: 13,
                padding: '3px 8px',
                borderRadius: 5,
                letterSpacing: 0.8,
              }}
            >
              {scene.badge}
            </span>
            <span style={{fontSize: 18, fontWeight: 700, color: '#f1f5f9'}}>
              {scene.title}
            </span>
          </div>
          <span
            style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 14,
              color: scene.badgeColor,
              fontWeight: 600,
            }}
          >
            {scene.formula}
          </span>
        </div>

        <div
          style={{
            fontSize: 15.5,
            lineHeight: 1.35,
            color: '#cbd5e1',
            marginBottom: 6,
          }}
        >
          {scene.narration}
        </div>

        <div
          style={{
            width: '100%',
            height: 4,
            backgroundColor: 'rgba(148, 163, 184, 0.2)',
            borderRadius: 2,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${progress}%`,
              height: '100%',
              backgroundColor: scene.badgeColor,
            }}
          />
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const MyComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#080c14'}}>
      <Series>
        {SCENES.map((sc) => (
          <Series.Sequence key={sc.id} durationInFrames={sc.durationInFrames}>
            <SceneSlide scene={sc} />
          </Series.Sequence>
        ))}
      </Series>
    </AbsoluteFill>
  );
};
