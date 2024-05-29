/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import {createBrowserRouter, RouterProvider} from 'react-router-dom';

import HomePage from "./pages/Home.page.tsx";

import KairyouPage from "./pages/Kairyou.page.tsx";

import OkisouchiPage from './pages/Okisouchi.page.tsx';
import OkisouchiTermsOfServicePage from './pages/okisouchi_mds/Okisouchi.tos.page.tsx';
import OkisouchiPrivacyPolicyPage from './pages/okisouchi_mds/Okisouchi.privacypolicy.tsx';
import OkisouchiLicensePage from './pages/okisouchi_mds/Okisouchi.license.tsx';

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
        path: '/okisouchi',
        element: <OkisouchiPage/>,
    },
    {
        path: '/okisouchi/tos',
        element: <OkisouchiTermsOfServicePage/>,
    },
    {
        path: '/okisouchi/privacy',
        element: <OkisouchiPrivacyPolicyPage/>,
    },
    {
        path: '/okisouchi/license',
        element: <OkisouchiLicensePage/>,
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
