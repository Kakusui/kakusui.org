/*
Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
Use of this source code is governed by an GNU Affero General Public License v3.0
license that can be found in the LICENSE file.
*/

import {
    chakra,
    GridItem,
    TextProps,
} from "@chakra-ui/react";

interface FeatureProps 
{
    heading: string;
    text: string;
    color: TextProps['color'];
}

const Feature = ({heading, text, color}: FeatureProps) => 
{
    return (
        <GridItem>
            <chakra.h3 fontSize="xl" fontWeight="600" color={"white"}>
                {heading}
            </chakra.h3>
            <chakra.p color={color}>{text}</chakra.p>
        </GridItem>
    );
};

export default Feature;