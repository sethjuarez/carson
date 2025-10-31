import {
  type Edge,
  type Node,

} from "@xyflow/react";

export interface Item {
  id: string;
  name: string;
  description: string;
  type: string;
  default: boolean;
  data: any;
}

export interface DesignData {
  background: string;
  logo: string;
  title: string;
  subtitle: string;
  description: string;
}

export interface Design extends Item {
  type: "design";
  data: DesignData;
}

export interface AppNode extends Node {
  data: {
    prompt: string;
    label: string;
  };
}

export interface AppEdge extends Edge {
  data: {
    label: string;
    task: string;
  };
}

export interface WorkflowData {
  nodes: AppNode[];
  edges: AppEdge[];
}

export interface Workflow extends Item {
  type: "workflow";
  data: WorkflowData;
}