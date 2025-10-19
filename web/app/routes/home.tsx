import type { Route } from "./+types/home";
import styles from "./home.module.scss";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ];
}

export default function Home() {
  return <div className={styles.thing}>Hello world!</div>;
}
