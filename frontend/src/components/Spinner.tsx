export default function Spinner() {
    return (
        <div className="flex justify-center items-center py-8">
            <div
                className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-100"
                role="status"
            >
                <span className="sr-only">Loading...</span>
            </div>
        </div>
    );
}
