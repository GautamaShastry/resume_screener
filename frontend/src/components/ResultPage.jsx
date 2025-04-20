import { useLocation } from 'react-router-dom';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { useEffect, useState } from 'react';

ChartJS.register(ArcElement, Tooltip, Legend);

const ResultPage = () => {
    const { state } = useLocation();
    const [data, setData] = useState(null);

    useEffect(() => {
        if (state) {
        setData(state);
        }
    }, [state]);

    if (!data) return <div className="text-center mt-10 text-lg">Loading results...</div>;

    const pieData = {
        labels: ['Match %', 'Mismatch %'],
        datasets: [
        {
            data: [data.accuracy, 100 - data.accuracy],
            backgroundColor: ['#4ade80', '#f87171'], // green, red
            hoverOffset: 4,
        },
        ],
    };

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
        <h2 className="text-3xl font-bold mb-6">Resume Match Result</h2>

        <div className="bg-white p-8 rounded shadow-md w-full max-w-4xl flex flex-col md:flex-row items-center justify-around">
            {/* Left: Pie Chart */}
            <div className="w-72 h-72 mb-8 md:mb-0">
            <Pie data={pieData} />
            </div>

            {/* Right: Details */}
            <div className="flex flex-col space-y-4">
            <h3 className="text-2xl font-bold">Match Score: {data.accuracy}%</h3>

            <div>
                <h4 className="text-lg font-semibold mb-1">Top Strengths</h4>
                <ul className="list-disc ml-5">
                {data.strengths
                    ?.split(',')
                    .filter(Boolean)
                    .slice(0, 5)
                    .map((skill, idx) => (
                    <li key={idx}>{skill.trim()}</li>
                    ))}
                </ul>
            </div>

            <div>
                <h4 className="text-lg font-semibold mb-1">Top Weaknesses</h4>
                <ul className="list-disc ml-5">
                {data.weaknesses
                    ?.split(',')
                    .filter(Boolean)
                    .slice(0, 5)
                    .map((skill, idx) => (
                    <li key={idx}>{skill.trim()}</li>
                    ))}
                </ul>
            </div>
            </div>
        </div>
        </div>
    );
};

export default ResultPage;
