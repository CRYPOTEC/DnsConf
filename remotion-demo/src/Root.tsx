import {Composition} from 'remotion';
import {Demo} from './Demo';
import {SvoyVpn, TOTAL_DUR} from './svoy/SvoyVpn';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Demo"
        component={Demo}
        durationInFrames={150}
        fps={30}
        width={1280}
        height={720}
      />
      <Composition
        id="SvoyVpn"
        component={SvoyVpn}
        durationInFrames={TOTAL_DUR}
        fps={30}
        width={1280}
        height={720}
      />
    </>
  );
};
