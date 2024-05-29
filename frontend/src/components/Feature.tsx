// chakra-ui
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