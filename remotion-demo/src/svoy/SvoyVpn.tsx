import {
  AbsoluteFill,
  Easing,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

// Раскадровка (30 fps):
//  Сцена 1 — герой на фоне Земли представляется (hero.mp4, 0–5.6s)
//  Сцена 2 — «фото»: статичный логотип, наезд камеры
//  Сцена 3 — логотип искрит молниями (lightning.mp4)
//  Сцена 4 — герой «забрал» логотип: молнии погасли, рассказ о преимуществах (hero.mp4, 5.6–10s)
//  Финал  — логотип, слоган, затемнение
export const S1_DUR = 168;
export const S2_DUR = 114;
export const S3_DUR = 138;
export const S4_DUR = 130;
export const OUT_DUR = 120;
export const TOTAL_DUR = S1_DUR + S2_DUR + S3_DUR + S4_DUR + OUT_DUR;

const FONT = 'Helvetica, Arial, sans-serif';

// Реплика героя в комикс-стиле
const Bubble: React.FC<{
  text: string;
  appearAt: number;
  hideAt: number;
  top: number;
  left: number;
}> = ({text, appearAt, hideAt, top, left}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  if (frame < appearAt || frame > hideAt) {
    return null;
  }

  const pop = spring({
    frame: frame - appearAt,
    fps,
    config: {damping: 12, stiffness: 200},
  });
  const out = interpolate(frame, [hideAt - 8, hideAt], [1, 0], {
    extrapolateLeft: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left,
        maxWidth: 430,
        backgroundColor: 'white',
        borderRadius: 26,
        border: '5px solid #16213e',
        padding: '18px 26px',
        fontFamily: FONT,
        fontSize: 33,
        fontWeight: 800,
        color: '#16213e',
        transform: `scale(${pop})`,
        transformOrigin: 'bottom left',
        opacity: out,
        boxShadow: '0 8px 24px rgba(0,0,0,0.45)',
      }}
    >
      {text}
    </div>
  );
};

// Плашка-преимущество
const FeaturePill: React.FC<{
  text: string;
  appearAt: number;
  top: number;
}> = ({text, appearAt, top}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  if (frame < appearAt) {
    return null;
  }

  const pop = spring({
    frame: frame - appearAt,
    fps,
    config: {damping: 13, stiffness: 160},
  });

  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 40,
        backgroundColor: 'rgba(11, 25, 49, 0.88)',
        border: '3px solid #34d399',
        borderRadius: 999,
        padding: '14px 30px',
        fontFamily: FONT,
        fontSize: 34,
        fontWeight: 800,
        color: 'white',
        transform: `translateX(${(pop - 1) * 350}px)`,
        opacity: pop,
        boxShadow: '0 0 24px rgba(52, 211, 153, 0.45)',
      }}
    >
      {text}
    </div>
  );
};

// Круглый логотип, вырезанный из квадратного кадра lightning.mp4
const RoundLogo: React.FC<{size: number}> = ({size}) => {
  // Медальон занимает ~52% ширины исходного квадратного кадра и чуть смещён вверх
  const imgSize = size / 0.52;
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        overflow: 'hidden',
        position: 'relative',
        boxShadow: '0 0 40px rgba(52, 211, 153, 0.8), 0 0 80px rgba(52, 211, 153, 0.4)',
      }}
    >
      <Img
        src={staticFile('svoy/logo.png')}
        style={{
          position: 'absolute',
          width: imgSize,
          height: imgSize,
          left: (size - imgSize) / 2,
          top: (size - imgSize) / 2 + size * 0.04,
        }}
      />
    </div>
  );
};

const Scene1Hero: React.FC = () => {
  const frame = useCurrentFrame();

  const slideOut = interpolate(frame, [S1_DUR - 12, S1_DUR], [0, -1380], {
    extrapolateLeft: 'clamp',
    easing: Easing.in(Easing.cubic),
  });

  return (
    <AbsoluteFill style={{transform: `translateX(${slideOut}px)`}}>
      <OffthreadVideo
        src={staticFile('svoy/hero.mp4')}
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
      <Bubble
        text="Привет! Я — SvoyVPN, защитник твоего интернета! 🌍"
        appearAt={14}
        hideAt={85}
        top={70}
        left={60}
      />
      <Bubble
        text="Хочешь свой собственный VPN? Сейчас покажу моё секретное оружие…"
        appearAt={95}
        hideAt={S1_DUR - 8}
        top={70}
        left={760}
      />
    </AbsoluteFill>
  );
};

const Scene2Photo: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const slideIn = spring({
    frame,
    fps,
    config: {damping: 16, stiffness: 90},
  });
  const zoom = interpolate(frame, [0, S2_DUR], [1.0, 1.14]);
  const textIn = interpolate(frame, [20, 45], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        transform: `translateX(${(1 - slideIn) * 1380}px)`,
        backgroundColor: '#0b1931',
      }}
    >
      <Img
        src={staticFile('svoy/logo.png')}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${zoom})`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: 50,
          width: '100%',
          textAlign: 'center',
          fontFamily: FONT,
          opacity: textIn,
        }}
      >
        <div
          style={{
            display: 'inline-block',
            backgroundColor: 'rgba(11, 25, 49, 0.85)',
            borderRadius: 20,
            padding: '16px 40px',
            color: 'white',
            fontSize: 42,
            fontWeight: 800,
            border: '3px solid #34d399',
          }}
        >
          Вот оно — секретное оружие 👀
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Scene3Lightning: React.FC = () => {
  const frame = useCurrentFrame();

  const captionIn = interpolate(frame, [10, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shake =
    frame > 40 ? Math.sin(frame * 2.7) * interpolate(frame, [40, S3_DUR], [0, 6]) : 0;

  return (
    <AbsoluteFill style={{backgroundColor: '#0b1931'}}>
      {/* Размытая подложка на всю ширину кадра */}
      <OffthreadVideo
        src={staticFile('svoy/lightning.mp4')}
        muted
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          filter: 'blur(45px) brightness(0.5)',
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          transform: `translateX(${shake}px)`,
        }}
      >
        <OffthreadVideo
          src={staticFile('svoy/lightning.mp4')}
          style={{height: '100%', borderRadius: 8}}
        />
      </AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          top: 40,
          width: '100%',
          textAlign: 'center',
          fontFamily: FONT,
          fontSize: 46,
          fontWeight: 900,
          color: 'white',
          textShadow: '0 4px 18px rgba(0,0,0,0.8)',
          opacity: captionIn,
        }}
      >
        ⚡ Заряжен молниеносной мощью ⚡
      </div>
    </AbsoluteFill>
  );
};

const Scene4Pitch: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const logoIn = spring({
    frame: frame - 6,
    fps,
    config: {damping: 11, stiffness: 120},
  });
  const bob = Math.sin(frame / 9) * 8;

  return (
    <AbsoluteFill>
      <OffthreadVideo
        src={staticFile('svoy/hero.mp4')}
        startFrom={S1_DUR}
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
      {/* Логотип «в руках» героя: молнии погасли */}
      <div
        style={{
          position: 'absolute',
          right: 95,
          top: 235 + bob,
          transform: `scale(${logoIn}) rotate(${(1 - logoIn) * 90}deg)`,
        }}
      >
        <RoundLogo size={230} />
      </div>
      <Bubble
        text="Поймал! Молнии — под контролем 😎"
        appearAt={8}
        hideAt={70}
        top={62}
        left={60}
      />
      <FeaturePill text="⚡ Молниеносная скорость" appearAt={40} top={380} />
      <FeaturePill text="🔒 Надёжное шифрование" appearAt={70} top={460} />
      <FeaturePill text="🚫 Никаких логов и слежки" appearAt={100} top={540} />
    </AbsoluteFill>
  );
};

const SceneOutro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const logoIn = spring({
    frame,
    fps,
    config: {damping: 12, stiffness: 110},
  });
  const pulse = 1 + Math.sin(frame / 7) * 0.025;
  const textIn = interpolate(frame, [18, 40], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(frame, [OUT_DUR - 22, OUT_DUR], [1, 0], {
    extrapolateLeft: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <AbsoluteFill
        style={{
          opacity: fadeOut,
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Img
          src={staticFile('svoy/logo.png')}
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            filter: 'blur(50px) brightness(0.35)',
            transform: 'scale(1.2)',
          }}
        />
        <div style={{transform: `scale(${logoIn * pulse})`}}>
          <RoundLogo size={300} />
        </div>
        <div
          style={{
            position: 'relative',
            marginTop: 45,
            textAlign: 'center',
            fontFamily: FONT,
            opacity: textIn,
          }}
        >
          <div style={{fontSize: 64, fontWeight: 900, color: 'white'}}>
            SVOY VPN
          </div>
          <div
            style={{
              fontSize: 36,
              fontWeight: 700,
              color: '#34d399',
              marginTop: 12,
            }}
          >
            Твой собственный VPN — подключайся! 🚀
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// Белая вспышка-перебивка с пиком в указанном кадре
const Flash: React.FC<{at: number; strength?: number}> = ({
  at,
  strength = 1,
}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [at - 5, at, at + 9],
    [0, strength, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  if (opacity <= 0) {
    return null;
  }
  return <AbsoluteFill style={{backgroundColor: 'white', opacity}} />;
};

export const SvoyVpn: React.FC = () => {
  const t2 = S1_DUR;
  const t3 = S1_DUR + S2_DUR;
  const t4 = S1_DUR + S2_DUR + S3_DUR;
  const t5 = S1_DUR + S2_DUR + S3_DUR + S4_DUR;

  return (
    <AbsoluteFill style={{backgroundColor: '#0b1931'}}>
      <Sequence durationInFrames={S1_DUR} name="Герой представляется">
        <Scene1Hero />
      </Sequence>
      <Sequence from={t2} durationInFrames={S2_DUR} name="Фото логотипа">
        <Scene2Photo />
      </Sequence>
      <Sequence from={t3} durationInFrames={S3_DUR} name="Молнии">
        <Scene3Lightning />
      </Sequence>
      <Sequence from={t4} durationInFrames={S4_DUR} name="Преимущества">
        <Scene4Pitch />
      </Sequence>
      <Sequence from={t5} durationInFrames={OUT_DUR} name="Финал">
        <SceneOutro />
      </Sequence>
      <Flash at={t3} strength={0.85} />
      <Flash at={t4} strength={1} />
    </AbsoluteFill>
  );
};
