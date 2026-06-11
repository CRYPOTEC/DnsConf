import {Composition} from 'remotion';
import {Demo} from './Demo';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Demo"
      component={Demo}
      durationInFrames={150}
      fps={30}
      width={1280}
      height={720}
    />
  );
};
