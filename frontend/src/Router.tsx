/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import {createBrowserRouter, RouterProvider} from 'react-router-dom';
import HomePage from "./pages/Home.page.tsx";
import KairyouPage from "./pages/Kairyou.page.tsx";
import NotFoundPage from './pages/error_pages/404.tsx';
import ForbiddenPage from './pages/error_pages/403.tsx';
import InternalErrorPage from './pages/error_pages/500.tsx';

const router = createBrowserRouter([
    {
        path: '/',
        element: <HomePage/>,
    },
    {
        path: '/kairyou',
        element: <KairyouPage/>,
    },
    {
        path: '/403',
        element: <ForbiddenPage/>,
    },
    {
        path: '/500',
        element: <InternalErrorPage/>,
    },
    {
        path: '*',
        element: <NotFoundPage/>,
    },

]);

function Router() {
    return <RouterProvider router={router}/>;
}

export default Router;
