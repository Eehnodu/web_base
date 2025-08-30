import { createBrowserRouter } from "react-router-dom";
import Home from "../containers/Home/Home";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
]);
