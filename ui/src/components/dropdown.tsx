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
            <label className='block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2'>
                {label}
            </label>
            <select {...register(name)}
                    className='block appearance-none w-full bg-gray-200 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-gray-500'>
                {dropdownOptions}
            </select>
        </>
    )
};