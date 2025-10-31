import React from "react";
import styles from "./taskedge.module.scss";
import {
  type EdgeProps,
  type Edge,
  BaseEdge,
  getBezierPath,
  EdgeLabelRenderer,
  getStraightPath,
  getSmoothStepPath,
  MarkerType,
  Position,
} from "@xyflow/react";
import clsx from "clsx";

type TaskEdgeItem = Edge<
  {
    id: string;
    task: string;
  },
  "task"
>;

const TaskEdge: React.FC<EdgeProps<TaskEdgeItem>> = (
  props: EdgeProps<TaskEdgeItem>
) => {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX: props.sourceX,
    sourceY: props.sourceY,
    sourcePosition: Position.Right,
    targetX: props.targetX,
    targetY: props.targetY,
    targetPosition: Position.Left,
  });
  return (
    <>
      <BaseEdge
        id={props.data?.id}
        path={edgePath}
        markerEnd={props.markerEnd}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: "absolute",
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            pointerEvents: "all",
          }}
          className={clsx(styles.label, "nodrag", "nopan")}
        >
          {props.data?.task}
        </div>
      </EdgeLabelRenderer>
    </>
  );
};

export default TaskEdge;
