import {useForm} from "react-hook-form";
import {Input} from "./input";
import {Dropdown} from "./dropdown";
import {SearchInput} from "./search-input";

const RON = 'RON';
const EUR = 'EUR';
const CURRENCIES = {RON, EUR}

const WITHDRAWAL = 'Withdrawal';
const DEPOSIT = 'Deposit';
const TRANSFER = 'Transfer';
const TRANSFER_TYPES = {WITHDRAWAL, DEPOSIT, TRANSFER}

interface TransactionFormProps {
    onSubmit: (formValues: any) => any
}

const TransactionForm = ({onSubmit}: TransactionFormProps) => {
    const {register, handleSubmit} = useForm();

    return (
        <>
            <form onSubmit={handleSubmit(onSubmit)} className='w-full max-w-lg mt-2'>
                <div className="flex flex-wrap -mx-3 mb-6">
                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <Dropdown name={'transfer_type'} options={TRANSFER_TYPES} register={register}/>
                    </div>

                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <Input name='description' register={register}/>
                    </div>
                </div>

                <div>
                    <Input name='source_account' register={register}/>
                    <Input name='destination_account' register={register}/>
                </div>
                <div className="flex flex-wrap -mx-3 mb-6">
                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <Input name='date' type='date' register={register}/>
                    </div>

                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <SearchInput name='category' dataList={['test', 'category 2']} register={register}/>
                    </div>
                </div>

                <div className="flex flex-wrap -mx-3 mb-6">
                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <Input name='amount' type='number' register={register}/>

                    </div>
                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <Dropdown name='currency' options={CURRENCIES} register={register}/>
                    </div>

                </div>

                <div className="flex flex-wrap -mx-3 mb-6">
                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <Input name='foreign_amount' type='number' register={register}/>
                    </div>
                    <div className='w-full md:w-1/2 px-3 mb-6 md:mb-0'>
                        <Dropdown name='foreign_currency' options={CURRENCIES} register={register}/>
                    </div>
                </div>

                <div className="flex justify-center mt-6 mx-auto">
                    <input
                        type="submit"
                        className='flex-1 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline'
                    />
                </div>
            </form>
        </>
    );

}

export default TransactionForm;
