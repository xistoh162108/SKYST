import { createBrowserRouter, RouterProvider, Outlet } from "react-router-dom";

import { Home, Page404 } from "~pages";

import { pathKeys } from "~shared/lib/react-router/pathKey.js";

function Layout() {
    return (
        <>
            <Outlet />
        </>
    );
}

const routes = [{ pathKey: pathKeys.home.root(), element: <Home /> }];

const browserRouter = createBrowserRouter([
    {
        element: <Layout />,
        children: [...routes, { path: "*", element: <Page404 /> }],
    },
]);

export default function AppRouter() {
    return <RouterProvider router={browserRouter} />;
}
