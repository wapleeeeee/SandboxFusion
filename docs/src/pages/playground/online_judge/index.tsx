import React from "react";
import OnlineJudgePage from "../../../components/playground/online_judge";
import PlaygroundLayout from "../layout";

const OnlineJudge: React.FC = () => {
  return <PlaygroundLayout Children={OnlineJudgePage} />;
};

OnlineJudge.displayName = "OnlineJudge";

export default React.memo(OnlineJudge);
