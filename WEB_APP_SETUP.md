# Flight Price Aggregator - Web Application Setup Guide

A professional, production-ready web application for searching and comparing flights across multiple providers using the CrewAI-powered flight search API.

## 📋 Overview

The web application provides users with an intuitive interface to:
- Search for flights by source, destination, departure date, number of passengers, and cabin class
- Compare prices across 4 flight providers (Skyscanner, Kayak, Google Flights, Amadeus)
- Sort flights by price, duration, or number of stops
- View detailed flight information (airline, times, duration, available seats)
- Book flights directly through provider booking links

## 🚀 Quick Start

### Option 1: Standalone HTML (Easiest)

1. **Make sure your FastAPI backend is running:**
   ```bash
   # In your FastAPI directory
   python main_agents.py
   ```
   The API should be accessible at `http://localhost:8080`

2. **Open the web app in your browser:**
   - Simply open `index.html` in your web browser
   - Or use a simple HTTP server:
     ```bash
     # From the project directory
     python -m http.server 8000
     ```
   - Then navigate to `http://localhost:8000/index.html`

### Option 2: React Component (For React/Next.js Projects)

If you're using React or Next.js:

```bash
npm install lucide-react
```

Then import and use the component:

```jsx
import FlightSearchApp from './flight_search_app';

export default function Page() {
  return <FlightSearchApp />;
}
```

## 🎨 Features

### User Interface
- **Clean, modern design** with Tailwind CSS
- **Responsive layout** - works on desktop, tablet, and mobile
- **Real-time form validation** with helpful error messages
- **Loading states** with animated spinners
- **Empty state messaging** for better UX

### Search Functionality
- **Airport code input** (e.g., JFK, LAX, LHR)
- **Date picker** for departure date
- **Passenger selection** (1-9 passengers)
- **Cabin class selector** (Economy, Business, First)
- **Form validation** with specific error messages

### Results Display
- **Flight cards** showing detailed information:
  - Provider name and airline
  - Flight number and departure/arrival times
  - Flight duration and number of stops
  - Available seats
  - Price per passenger and total price
  - Direct booking link
  
- **Smart sorting options:**
  - **Cheapest** - Sort by lowest price
  - **Fastest** - Sort by shortest duration
  - **Fewest Stops** - Sort by minimum connections

- **Color-coded providers:**
  - 🔵 Skyscanner (Blue)
  - 🟠 Kayak (Orange)
  - 🟢 Google Flights (Green)
  - 🟣 Amadeus (Purple)

### Error Handling
- API connection errors with helpful messages
- Form validation with specific guidance
- Empty results with suggestions
- Network error recovery

## 🔧 Technical Architecture

### Frontend Stack
- **React 18** - UI framework
- **Tailwind CSS** - Styling and responsive design
- **Lucide React Icons** - Beautiful, consistent iconography
- **Vanilla JavaScript** - No build tools required

### Component Structure

```
FlightSearchApp
├── State Management (useState, useCallback)
├── Search Form
│   ├── Airport inputs
│   ├── Date picker
│   ├── Passenger selector
│   ├── Cabin class selector
│   └── Search button
├── Results Section
│   ├── Sort controls
│   ├── Flight cards
│   └── Booking links
└── Error handling & loading states
```

### API Integration

The app communicates with the FastAPI backend:

```
POST /api/v1/flights/search

Request:
{
  "origin": "JFK",
  "destination": "LAX",
  "departure_date": "2024-12-25",
  "passengers": 2,
  "cabin_class": "economy"
}

Response:
{
  "flights": [...],
  "total_results": 45,
  "search_params": {...},
  "provider_results": {...}
}
```

## 📱 Usage Guide

### Searching for Flights

1. **Enter departure airport** (3-letter IATA code)
2. **Enter arrival airport** (3-letter IATA code)
3. **Select departure date** using the date picker
4. **Choose number of passengers** (1-9)
5. **Select cabin class** (Economy, Business, First)
6. **Click Search** or press Enter

### Viewing Results

- Results appear sorted by **price (cheapest first)** by default
- **Toggle sorting** using buttons: Cheapest, Fastest, Fewest Stops
- Each flight card shows all relevant details
- Click **"Book Now"** to book on the provider's website

### Error Handling

If you encounter errors:
- **"API Error"**: Make sure `python main_agents.py` is running on localhost:8080
- **"No flights found"**: Try different dates or airport codes
- **"Connection error"**: Check that the FastAPI backend is accessible

## 🛠️ Troubleshooting

### Issue: "Failed to connect to API"
**Solution:** 
- Ensure FastAPI backend is running: `python main_agents.py`
- Check that it's accessible at `http://localhost:8080`
- Verify CORS is enabled (should be in main_agents.py)

### Issue: Flights not loading
**Solution:**
- Try different airport codes (use valid IATA codes)
- Try a different departure date (use YYYY-MM-DD format)
- Check browser console (F12) for detailed error messages

### Issue: "CORS Error"
**Solution:**
- The backend already has CORS enabled
- Try accessing from a different browser or private window
- Check that you're using the correct API endpoint

## 📊 Performance

- **Fast searches** - Typically returns results in 5-10 seconds
- **Optimized rendering** - React efficiently updates only changed elements
- **Responsive design** - Works smoothly on all screen sizes
- **Error recovery** - Graceful handling of network failures

## 🔐 Security

- **No sensitive data stored** - All data sent via HTTPS-compatible requests
- **Input validation** - All user inputs are validated before sending
- **Safe external links** - Booking links open in new tabs with `rel="noopener noreferrer"`
- **CORS protection** - API validates origin and headers

## 📈 Future Enhancements

Potential improvements:
- Round-trip flights support
- Advanced filters (departure time, airline preference, price range)
- Favorite/saved flights
- Price alerts and notifications
- User account and booking history
- Payment integration
- Multi-language support

## 🧑‍💼 Production Deployment

### Deploy to Vercel (Recommended)
```bash
# Create a Vercel project from your GitHub repo
# The app works as a static site
```

### Deploy to Netlify
```bash
# Simply drag and drop the HTML file
# Or connect your GitHub repo
```

### Deploy to Your Own Server
```bash
# Copy files to your server
# Update API endpoint in the code if needed
# Serve via any HTTP server (Apache, Nginx, etc.)
```

## 📝 Configuration

To change the API endpoint, modify this line in the code:

```javascript
const response = await fetch('http://localhost:8080/api/v1/flights/search', {
```

Change `http://localhost:8080` to your actual API endpoint.

## 🎓 Learning Resources

- **React Documentation**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Lucide Icons**: https://lucide.dev
- **FastAPI**: https://fastapi.tiangolo.com

## 📄 License

This web application is part of the Flight Price Aggregator system. Use and modify as needed for your project.

## 🤝 Support

For issues or questions:
1. Check the error message carefully - it usually indicates the problem
2. Verify the API is running and accessible
3. Check browser console (F12) for JavaScript errors
4. Review the troubleshooting section above

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Built with:** React + Tailwind CSS + FastAPI
