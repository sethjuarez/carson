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

  const setOutputDimentsion = debounce(
    (ref: React.RefObject<HTMLDivElement | null>) => {
      if (ref.current) {
        setWidth(ref.current.clientWidth);
        setHeight(ref.current.clientHeight);
      }
    },
    10
  );

  useEffect(() => {
    work?.addRoot(scenarioOutput);
    window.addEventListener("resize", () => {
      setOutputDimentsion(chartRef);
    });
    return () => {
      window.removeEventListener("resize", () => {
        setOutputDimentsion(chartRef);
      });
    };
  }, [work]);

  useEffect(() => {
    setOutputDimentsion(chartRef);
  }, [chartRef]);

  function collapseToggled(): void {
    setOutputDimentsion(chartRef);
  }

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
            onToggleCollapse={collapseToggled}
          >
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
            onToggleCollapse={collapseToggled}
          >
            <Workflow />
          </Panel>
        </div>
        <div className={styles.effort}></div>
      </div>
    </main>
  );
}
