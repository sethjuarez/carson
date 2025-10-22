import type { Route } from "./+types/app";
import styles from "./app.module.scss";
import { useUser } from "store/useuser";
import { BiExpandVertical } from "react-icons/bi";
import { IoSparkles, IoGitBranchOutline } from "react-icons/io5";
import Title from "components/structure/title";
import Panel from "components/structure/panel";
import Tool from "components/structure/tool";
import Workflow from "components/workflow/workflow";
import Output from "components/output/output";
import usePersistStore from "store/usepersiststore";
import { useOutputStore } from "store/output";
import { useEffect } from "react";
import { scenarioOutput } from "store/data";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Carson - Your AI Butler" },
    { name: "description", content: "Welcome to Carson!" },
  ];
}

export default function App() {
  const title = "Carson";
  const sub_title = "Your AI Butler";
  const version = "v0.8.3";
  const logo = "/images/tuxedo.svg";
  const work = usePersistStore(useOutputStore, (state) => state);
  const { user, error } = useUser();

  // load default data if no work present using useEffect
  useEffect(() => {
    work?.addRoot(scenarioOutput);
  }, [work]);

  return (
    <main className={styles.home}>
      <Title
        text={title}
        subtitle={sub_title}
        version={version}
        logo={logo}
        user={user}
      />
      <div className={styles.container}>
        <div className={styles.content}>
          <Panel
            icon={<IoSparkles size={16} />}
            header="Work Panel"
            actions={
              <Tool
                icon={<BiExpandVertical size={16} />}
                onClick={() => alert("CLICK")}
              />
            }
          >
            <div className={styles.output}>
              {work && work.output && work.output.children.length > 0 && (
                <Output data={work.output} />
              )}
            </div>
          </Panel>
          <Panel
            icon={<IoGitBranchOutline size={16} />}
            header="Voice Workflow"
            actions={
              <Tool
                icon={<BiExpandVertical size={16} />}
                onClick={() => alert("CLICK")}
              />
            }
          >
            <Workflow />
          </Panel>
        </div>
        <div className={styles.sidebar}></div>
      </div>
    </main>
  );
}
