import React from 'react';
import {Composition} from 'remotion';
import {MyComposition, SCENES} from './Composition';

const totalDuration = SCENES.reduce((acc, s) => acc + s.durationInFrames, 0);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="TernaryCNFETExplainer"
        component={MyComposition}
        durationInFrames={totalDuration}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
