import { useEffect, useState } from "react";
import "./App.css";

import { getCompanies } from "./api/companyApi";

function App() {

    const [companies, setCompanies] = useState([]);

    useEffect(() => {

        async function loadCompanies() {

            try {
                const data = await getCompanies();
                setCompanies(data);

            } catch (error) {

                console.error(error);

            }

        }

        loadCompanies();

    }, []);

    return (

        <div className="app">

            <header className="header">

                <h1>🚀 AI Agency</h1>

                <p>Assistant commercial intelligent</p>

            </header>

            <div className="cards">

                <div className="card">
                    <h2>🏢 Entreprises</h2>
                    <p>{companies.length}</p>
                </div>

                <div className="card">
                    <h2>📊 Audits</h2>
                    <p>--</p>
                </div>

                <div className="card">
                    <h2>⭐ Scores</h2>
                    <p>--</p>
                </div>

                <div className="card">
                    <h2>✉️ Emails</h2>
                    <p>--</p>
                </div>

            </div>

            <h2 style={{ marginTop: 60 }}>

                Entreprises

            </h2>

            <table>

                <thead>

                    <tr>

                        <th>Nom</th>

                        <th>Ville</th>

                        <th>Secteur</th>

                        <th>Site</th>

                    </tr>

                </thead>

                <tbody>

                    {companies.map(company => (

                        <tr key={company.id}>

                            <td>{company.name}</td>

                            <td>{company.city}</td>

                            <td>{company.sector}</td>

                            <td>{company.website}</td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>

    );

}

export default App;