import type { Route } from "./+types/app";
import styles from "./app.module.scss";
import { useUser } from "store/useuser";
import { IoSparkles, IoGitBranchOutline } from "react-icons/io5";
import Title from "components/structure/title";
import Panel from "components/structure/panel";
import Workflow from "components/workflow/workflow";
import Output from "components/output/output";
import usePersistStore from "store/usepersiststore";
import { useOutputStore } from "store/output";
import { useEffect, useRef, useState } from "react";
import { scenarioOutput } from "store/data";
import { debounce } from "store/utils";
import Settings from "components/settings/settings";
import Setting from "components/settings/setting";
import { TbArticle, TbAssembly, TbSettingsCog } from "react-icons/tb";
import Tool from "components/structure/tool";

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

  const chartRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [height, setHeight] = useState(0);

  const setOutputDimentsion = debounce((entries: ResizeObserverEntry[]) => {
    if (entries[0].target) {
      setWidth(entries[0].contentRect.width);
      setHeight(entries[0].contentRect.height);
    }
  }, 10);

  useEffect(() => {
    work?.addRoot(scenarioOutput);

    const resizeObserver = new ResizeObserver(setOutputDimentsion);

    if (chartRef.current) {
      resizeObserver.observe(chartRef.current);
    }

    return () => {
      resizeObserver.disconnect();
    };
  }, [work, chartRef]);

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
          <Panel icon={<IoSparkles size={16} />} header="Work Panel">
            <div className={styles.output} ref={chartRef}>
              {work && work.output && work.output.children.length > 0 && (
                <Output data={work.output} height={height} width={width} />
              )}
            </div>
          </Panel>
          <Panel
            icon={<IoGitBranchOutline size={16} />}
            header="Voice Workflow"
            collapsed={true}
          >
            <Workflow />
          </Panel>
        </div>
        <div className={styles.effort}></div>
        <div className={styles.toolbar}>
          <Settings>
            <Tool
              icon={<TbSettingsCog size={14} />}
              onClick={() => alert("Tool clicked")}
              title={"Settings"}
            />
            <Setting
              id={"voice-agent-settings"}
              icon={<TbArticle size={14} />}
              className={styles.editor}
              title={"Voice Agent Settings"}
            >
              <div>Voice Agent Settings Component</div>
            </Setting>
            <Setting
              id={"design-settings"}
              icon={<TbAssembly size={14} />}
              className={styles.design}
              title={"Design Settings"}
            >
              <div>Design Settings Component</div>
            </Setting>
            <Setting
              id={"voice-settings"}
              icon={<TbSettingsCog size={14} />}
              className={styles.voice}
              title={"Voice Settings"}
            >
              <div>Voice Settings Component</div>
            </Setting>
          </Settings>
        </div>
      </div>
    </main>
  );
}
