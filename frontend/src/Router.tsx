import {createBrowserRouter, RouterProvider} from 'react-router-dom';
import HomePage from "./pages/Home.page.tsx";
import KairyouPage from "./pages/Kairyou.page.tsx";

const router = createBrowserRouter([
    {
        path: '/',
        element: <HomePage/>,
    },
    {
        path: '/kairyou',
        element: <KairyouPage/>,
    }
]);

function Router() {
    return <RouterProvider router={router}/>;
}

export default Router;