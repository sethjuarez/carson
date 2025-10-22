import React, { type ReactElement } from "react";
import styles from "./panel.module.scss";
import type Tool from "./tool";

type PanelProps = {
  header: string;
  icon?: React.ReactNode;
  actions?: ReactElement<typeof Tool> | ReactElement<typeof Tool>[];
  children?: React.ReactNode;
};

const Panel: React.FC<PanelProps> = ({ header, icon, actions, children }) => {
  if (!actions) {
    actions = [];
  }
  if (!Array.isArray(actions)) {
    actions = [actions];
  }
  return (
    <div className={styles.panel}>
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
        </div>
      </div>
      <div className={styles.content}>{children}</div>
    </div>
  );
};

export default Panel;
