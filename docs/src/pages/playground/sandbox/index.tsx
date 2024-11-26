import React from "react";
import SandboxPage from "../../../components/playground/sandbox";
import PlaygroundLayout from "../layout";

const Sandbox: React.FC = () => {
  return <PlaygroundLayout Children={SandboxPage} />;
};

Sandbox.displayName = "Sandbox";

export default React.memo(Sandbox);
