import {capitalizeFirstLetter} from "../utils/string";

interface DropdownProps {
    name: string,
    options: {
        [key: string]: string
    },
    register: Function
}

export const Dropdown = ({name, options, register}: DropdownProps) => {
    const label = capitalizeFirstLetter(name).replace('_', ' ');
    const dropdownOptions = Object.entries(options).map(
        ([value, label]) => <option value={value}>{label}</option>);

    return (
        <>
            <label>{label}</label>
            <select {...register(name)}>
                {dropdownOptions}
            </select>
        </>
    )
};