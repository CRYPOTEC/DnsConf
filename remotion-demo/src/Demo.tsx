import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const Particle: React.FC<{index: number}> = ({index}) => {
  const frame = useCurrentFrame();
  const {width, height, durationInFrames} = useVideoConfig();

  // Deterministic pseudo-random placement per particle
  const seed = (index * 9301 + 49297) % 233280;
  const x = (seed / 233280) * width;
  const size = 8 + (index % 5) * 6;
  const speed = 1 + (index % 4) * 0.5;
  const y = height - ((frame * speed + index * 60) % (height + 100));

  const opacity = interpolate(
    frame,
    [0, 20, durationInFrames - 30, durationInFrames],
    [0, 0.5, 0.5, 0],
  );

  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: size,
        height: size,
        borderRadius: '50%',
        backgroundColor: 'white',
        opacity,
      }}
    />
  );
};

export const Demo: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();

  const titleScale = spring({
    frame,
    fps,
    config: {damping: 10, stiffness: 100},
  });

  // Gentle pulse after the title lands
  const pulse = 1 + Math.sin(frame / 8) * 0.03;

  const subtitleOpacity = interpolate(frame, [40, 70], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const subtitleY = interpolate(frame, [40, 70], [30, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const fadeOut = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    {extrapolateLeft: 'clamp'},
  );

  const gradientShift = interpolate(frame, [0, durationInFrames], [0, 60]);

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${135 + gradientShift}deg, #1e3a8a 0%, #7c3aed 50%, #db2777 100%)`,
        justifyContent: 'center',
        alignItems: 'center',
        fontFamily: 'Helvetica, Arial, sans-serif',
        opacity: fadeOut,
      }}
    >
      {Array.from({length: 20}, (_, i) => (
        <Particle key={i} index={i} />
      ))}
      <h1
        style={{
          color: 'white',
          fontSize: 130,
          fontWeight: 800,
          margin: 0,
          transform: `scale(${titleScale * pulse})`,
          textShadow: '0 10px 40px rgba(0,0,0,0.4)',
        }}
      >
        Remotion
      </h1>
      <p
        style={{
          color: 'rgba(255,255,255,0.85)',
          fontSize: 40,
          marginTop: 30,
          opacity: subtitleOpacity,
          transform: `translateY(${subtitleY}px)`,
        }}
      >
        Видео, написанное кодом 🎬
      </p>
    </AbsoluteFill>
  );
};
