import React, { Component } from 'react';
import './App.css';

class Search extends Component {
    constructor(props){
        super(props);
        this.state = {
            search_query: '',
            results: [],
            typing: 0
        }
    }

    onChangeQuery = (e)=>{
        const {target: {value, name}} = e;
        if(this.state.typing){
            clearTimeout(this.state.typing);
        }
        this.setState({
            [name]: value,
            results: [],
            typing: setTimeout(()=>
                {
                    if(this.state.search_query !== ''){
                        this.fetchMovies(this.state.search_query);
                    }
                }, 300)
        });
    }

    fetchMovies = (query) => {
        fetch(`http://localhost:5000/search?query=${query}`)
        .then(response => response.json())
        .then(result => this.setState({results: [...result]}))
        .catch(error => console.log(error));
    }

    submitForm = (e)=>{
        e.preventDefault();
        this.fetchMovies(this.state.search_query);
    }

    addEntry = () =>{
        this.setState({
            search_query: '',
            results: []
        })
    }
    render(){
        return(
            <div className="Search">
                <form onSubmit={this.submitForm}>
                    <div className="form-group">
                        <input type="text" 
                            name="search_query"
                            className="form-control" 
                            placeholder="Search you movies" 
                            value={this.state.search_query}
                            onChange={this.onChangeQuery}/>
                    </div>
                </form>
                <div className="Search-Result">
                    {this.state.results.map(item => 
                        <div key={item.movieId} className="Search-Row">
                            <span>{item.title}</span>
                            <button type="button" className="btn btn-danger" 
                            onClick={()=> {this.props.addHistory(item.movieId, item.title); this.addEntry();}}>Add</button>                        
                        </div>
                    )}
                </div>
            </div>
        );
    }
}

class History extends Component {
    render(){
        return(
            <div className="History">
                {this.props.history.length > 0 && <h2>Your movies</h2>}
                {this.props.history.map(item => 
                    <button key={item.movieId} className="btn btn-info">{item.title}</button>    
                )}
            </div>
        );
    }
}

class Recommend extends Component {
    render(){
        return(
            <div className="container">
                <div className="row">
                    {this.props.isloading && <h2 className="Loading">Loading...</h2>}
                </div>
                <div className="Recommend row">
                {this.props.movie_list.map(item => 
                    <div className="card col-md-3" key={item.movieId}>
                        <img className="card-img-top" src={item.url} alt=""/>
                        <div className="card-body">
                            <h5 className="card-title">{item.title}</h5>
                        </div>
                    </div>
                )}
                </div>
            </div>
        );
    }
}

class App extends Component {
    constructor(props){
        super(props);
        this.state = {
            history_movies: [],
            recommmend_movies: [],
            loading: false
        }
    }

    addHistory = (id, title) => {
        const entry = {
            movieId: id,
            title: title
        }
        this.setState({
            history_movies: [...this.state.history_movies, entry]
        })
    }

    getMovies = ()=>{
        const id_list = this.state.history_movies.map(item => item.movieId);
        let data = "";
        for(let i = 0; i < id_list.length; i++){
            data += id_list[i];
            if(i !== id_list.length-1) data += " ";
        }
        this.setState({loading: true});
        fetch(`http://localhost:5000/recommend?ids=${data}`)
        .then(response => response.json())
        .then(response => this.setState({recommmend_movies: [...response], loading: false}));
    }

    clearHistory = ()=>{
        this.setState({
            recommmend_movies: [],
            history_movies: []
        });
    }

    render() {
        return (
            <div className="App">
                <header className="App-header">
                    <h1>What to watch next ?</h1>
                </header>
                <Search addHistory={this.addHistory}/>
                <History history={this.state.history_movies}/>
                <div className="container">
                    <div className="row">
                        {this.state.history_movies.length > 0 &&
                            <div className="Re"><button className="btn btn-success Get-Movie" 
                            onClick={this.getMovies}>Get Movies</button>
                            <button className="btn btn-danger"
                            onClick={this.clearHistory}>Clear History</button></div>
                        }
                    </div>
                </div>
                <Recommend movie_list={this.state.recommmend_movies} isloading={this.state.loading}/>
            </div>
        );
    }
}

export default App;
