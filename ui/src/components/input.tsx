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
            <label>{label}</label>
            <input {...register(name)} type={!!type && type}/>
        </>
    )
};