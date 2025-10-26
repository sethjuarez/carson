import React, { useState, type ReactElement } from "react";
import styles from "./panel.module.scss";
import Tool from "./tool";
import { BiExpandVertical } from "react-icons/bi";
import { clsx } from "clsx";

type PanelProps = {
  header: string;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  icon?: React.ReactNode;
  actions?: React.ReactNode[];
  children?: React.ReactNode;
};

const Panel: React.FC<PanelProps> = ({
  header,
  collapsed,
  onToggleCollapse,
  icon,
  actions,
  children,
}) => {
  const [hidden, setHidden] = useState(collapsed);

  const toggleDisclosure = () => {
    setHidden((prev) => !prev);
    onToggleCollapse?.();
  };

  if (!actions) {
    actions = [];
  }
  if (!Array.isArray(actions)) {
    actions = [actions];
  }
  return (
    <>
      <div className={styles.header}>
        {icon && <div className={styles.icon}>{icon}</div>}
        <div className={styles.title}>{header}</div>
        <div className={styles.spacer} />
        <div className={styles.actions}>
          {actions &&
            actions.map((action, index) => (
              <span key={index} className={styles.action}>
                {action}
              </span>
            ))}
          <BiExpandVertical
            size={16}
            onClick={toggleDisclosure}
            className={styles.action}
          />
        </div>
      </div>
      <div className={clsx(hidden ? styles.hidden : styles.content)}>
        {children}
      </div>
    </>
  );
};

export default Panel;
