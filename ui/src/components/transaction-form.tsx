import {useForm} from "react-hook-form";
import {Input} from "./input";
import {Dropdown} from "./dropdown";
import {SearchInput} from "./search-input";
import {TextArea} from "./textarea";
import {useEffect} from "react";
import {NumberInput} from "./number-input";
import {WarningIcon} from "./icons";

const RON = 'RON';
const EUR = 'EUR';
const CURRENCIES = {RON, EUR}

const TRANSFER_TYPES = {
    withdrawal: 'Withdrawal',
    deposit: 'Deposit',
    transfer: 'Transfer'
}

interface TransactionFormProps {
    onSubmit: (formValues: any) => any
    defaultValues?: {
        [key: string]: any
    },
    accounts?: string[];
    categories?: string[];
    descriptions?: string[];
}

const FORM_DEFAULT_VALUES = {
    "external_id": "",
    "description": "",
    "date": "",
    "source_account": "",
    "destination_account": "",
    "amount": 0,
    "type": "deposit",
    "category_name": "",
    "currency_code": "RON",
    "foreign_amount": null,
    "foreign_currency_code": null,
    "notes": "",
}
const TransactionForm = ({onSubmit, defaultValues, accounts, categories, descriptions}: TransactionFormProps) => {
    if (defaultValues == null) {
        defaultValues = FORM_DEFAULT_VALUES;
    } else {
        const parsedDate = new Date(defaultValues.date);
        let month = parsedDate.getMonth() + 1
        const strMonth = `${month < 10 ? '0' : ''}${month}`;
        const day = parsedDate.getDate();
        const strDay = `${day < 10 ? '0' : ''}${day}`;
        defaultValues.date = `${parsedDate.getFullYear()}-${strMonth}-${strDay}`
    }

    const {register, handleSubmit, reset} = useForm({defaultValues});
    const accountsNames = accounts != null ? accounts : [];
    const categoryNames = categories != null ? categories : [];
    descriptions = descriptions != null ? descriptions : [];

    useEffect(() => {
        if (defaultValues == null) {
            reset(FORM_DEFAULT_VALUES);
        } else {
            reset(defaultValues)
        }

    }, [defaultValues])


    const isUnknownDestinationAccount = defaultValues?.destination_account != null &&
        defaultValues?.destination_account.toLowerCase().includes('unknown');
    const isUnknownSourceAccount = defaultValues?.source_account != null &&
        defaultValues?.source_account.toLowerCase().includes('unknown');

    return (
        <form onSubmit={handleSubmit(onSubmit)} className='w-full max-w-lg mt-2'>
            <div className="flex flex-wrap -mx-3 mb-6">
                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <Dropdown name='type' options={TRANSFER_TYPES} register={register}/>
                </div>

                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <SearchInput name='description' dataList={descriptions} register={register} required/>
                </div>
            </div>

            <div>
                {isUnknownSourceAccount ? <WarningIcon/> : null}
                <SearchInput name='source_account' dataList={accountsNames} register={register}/>
                {isUnknownDestinationAccount ? <WarningIcon/> : null}
                <SearchInput name='destination_account' dataList={accountsNames} register={register}/>
            </div>
            <div className="flex flex-wrap -mx-3 mb-6">
                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <Input name='date' type='date' register={register}/>
                </div>

                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <SearchInput name='category_name' dataList={categoryNames} register={register}/>
                </div>
            </div>

            <div className="flex flex-wrap -mx-3 mb-6">
                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <NumberInput name='amount' pattern='^\d*(\.\d{0,2})?$' register={register}/>

                </div>
                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <Dropdown name='currency_code' options={CURRENCIES} register={register}/>
                </div>

            </div>

            <div className="flex flex-wrap -mx-3 mb-6">
                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <NumberInput name='foreign_amount' pattern='^\d*(\.\d{0,2})?$' register={register}/>
                </div>
                <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                    <Dropdown name='foreign_currency_code' options={CURRENCIES} register={register}/>
                </div>
            </div>

            <div>
                <TextArea name='notes' register={register}/>
            </div>

            <div className="flex justify-center mt-6 mx-auto">
                <input
                    type="submit"
                    className='flex-1 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline'
                />
            </div>
        </form>
    );

}

export default TransactionForm;
