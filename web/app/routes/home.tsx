import type { Route } from "./+types/home";
import styles from "./home.module.scss";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Carson - Your AI Butler" },
    { name: "description", content: "Welcome to Carson!" },
  ];
}

export default function Home() {
  return <div className={styles.frame}>HOME</div>;
}
