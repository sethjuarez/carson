import type { Route } from "./+types/favicon";
import { FaDiceD6 } from "react-icons/fa6";
import { renderToString } from "react-dom/server";

export async function loader({ params }: Route.LoaderArgs) {
  return new Response(
    renderToString(<FaDiceD6 size={32} style={{ color: "#0ea5e9" }} />),
    {
      status: 200,
      headers: {
        "Content-Type": "image/svg+xml",
      },
    }
  );
}
