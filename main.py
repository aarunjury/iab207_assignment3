from bookings import create_app

if __name__=='__main__':
    n_app=create_app()
    n_app.run(debug=True,host="0.0.0.0")