// Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
// Use of this source code is governed by an GNU Affero General Public License v3.0
// license that can be found in the LICENSE file.

// maintain allman bracket style for consistency

//react
import React from 'react'
import ReactDOM from 'react-dom/client'

// Custom
import ServiceClosed from './ServiceClosed'

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ServiceClosed />
    </React.StrictMode>,
)
