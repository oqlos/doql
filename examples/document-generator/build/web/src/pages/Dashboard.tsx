import React from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';

export default function Dashboard() {
  const [counts, setCounts] = React.useState<Record<string, number>>({}); 

  React.useEffect(() => {

  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Calibration Certificate Generator</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

      </div>
    </div>
  );
}
