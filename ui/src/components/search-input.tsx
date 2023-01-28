import {capitalizeFirstLetter} from "../utils/string";

interface SearchInputProps {
    name: string;
    register: Function;
    dataList: string[];
    required?: boolean;
}


export const SearchInput = ({name, register, dataList, required = false}: SearchInputProps) => {
    const label = capitalizeFirstLetter(name).replace('_', ' ');
    const dataListId = `${name}-datalist`;
    return (
        <>
            <datalist id={dataListId}>
                {dataList.map((item, idx) => <option key={idx} value={item}/>)}
            </datalist>
            <label className='block uppercase tracking-wide text-gray-700 text-xs font-bold mb-2'>
                {label}
            </label>
            <input
                {...register(name)}
                type='search'
                list={dataListId}
                required={required}
                className='appearance-none block w-full bg-gray-200 text-gray-700 border border-red-500 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white'
            />
        </>
    )
};