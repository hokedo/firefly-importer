import {capitalizeFirstLetter} from "../utils/string";

interface InputProps {
    name: string;
    register: Function;
    type?: 'text' | 'number' | 'date';
}


export const Input = ({name, register, type}: InputProps) => {
    const label = capitalizeFirstLetter(name).replace('_', ' ');
    return (
        <>
            <label className='block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2'>
                {label}
            </label>
            <input
                {...register(name)}
                type={!!type && type}
                className='appearance-none block w-full bg-gray-200 text-gray-700 border border-red-500 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white'
            />
        </>
    )
};