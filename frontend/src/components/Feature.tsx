/*
Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
Use of this source code is governed by a GNU General Public License v3.0
license that can be found in the LICENSE file.
*/

import {
    chakra,
    GridItem,
} from "@chakra-ui/react";

interface FeatureProps {
    heading: string;
    text: string;
}

const Feature = ({heading, text}: FeatureProps) => {
    return (
        <GridItem>
            <chakra.h3 fontSize="xl" fontWeight="600">
                {heading}
            </chakra.h3>
            <chakra.p>{text}</chakra.p>
        </GridItem>
    );
};

export default Feature;