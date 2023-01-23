import {capitalizeFirstLetter} from "../utils/string";

interface SearchInputProps {
    name: string;
    register: Function;
    dataList: string[];
}


export const SearchInput = ({name, register, dataList}: SearchInputProps) => {
    const label = capitalizeFirstLetter(name).replace('_', ' ');
    const dataListId = `${name}-datalist`;
    return (
        <>
            <datalist id={dataListId}>
                {dataList.map(item => <option value={item}/>)}
            </datalist>
            <label>{label}</label>
            <input {...register(name)} type='search' list={dataListId}/>
        </>
    )
};