const Loading = () => {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
                <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
                <p className="mt-6 text-xl font-semibold text-blue-700">Loading...</p>
                </div>
            </div>
        );
};

export default Loading;
