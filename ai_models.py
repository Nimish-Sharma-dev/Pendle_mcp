"""
AI-powered yield prediction and market analysis for Pendle Finance.

This module provides intelligent recommendations based on real market data
including APY analysis, liquidity scoring, and risk assessment.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)


def predict_best_yield(markets_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Analyze market data and predict the best yield opportunity.
    
    Uses a weighted scoring algorithm:
    - 40% weight on impliedApy (fixed yield rate)
    - 30% weight on liquidity (higher is safer)
    - 20% weight on underlyingApy (base yield)
    - 10% weight on time to expiry (longer is better for fixed yield)
    
    Args:
        markets_data: List of market dictionaries from Pendle API
        
    Returns:
        Dictionary with predicted best token, expected yield, and reasoning
    """
    if not markets_data or len(markets_data) == 0:
        logger.warning("No market data provided for yield prediction")
        return {
            "predicted_best_token": "N/A",
            "expected_yield": "N/A",
            "reasoning": "No market data available",
            "confidence": "low",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    try:
        scored_markets = []
        
        for market in markets_data:
            try:
                # Extract key metrics
                symbol = market.get('proSymbol', 'Unknown')
                implied_apy = market.get('impliedApy', 0) * 100  # Convert to percentage
                underlying_apy = market.get('underlyingApy', 0) * 100
                liquidity_usd = market.get('liquidity', {}).get('usd', 0)
                expiry = market.get('expiry', '')
                protocol = market.get('protocol', 'Unknown')
                
                # Calculate days to expiry
                days_to_expiry = 0
                if expiry:
                    try:
                        expiry_date = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
                        days_to_expiry = (expiry_date - datetime.now(expiry_date.tzinfo)).days
                    except:
                        days_to_expiry = 0
                
                # Skip expired or very short-term markets
                if days_to_expiry < 7:
                    continue
                
                # Calculate weighted score
                apy_score = implied_apy * 0.4
                liquidity_score = min(liquidity_usd / 10_000_000, 10) * 0.3  # Normalize to 0-10 scale
                underlying_score = underlying_apy * 0.2
                expiry_score = min(days_to_expiry / 365, 1) * 10 * 0.1  # Normalize to 0-10 scale
                
                total_score = apy_score + liquidity_score + underlying_score + expiry_score
                
                scored_markets.append({
                    'symbol': symbol,
                    'protocol': protocol,
                    'implied_apy': round(implied_apy, 2),
                    'underlying_apy': round(underlying_apy, 2),
                    'liquidity_usd': liquidity_usd,
                    'days_to_expiry': days_to_expiry,
                    'score': total_score
                })
                
            except Exception as e:
                logger.warning(f"Error scoring market: {e}")
                continue
        
        if not scored_markets:
            return {
                "predicted_best_token": "N/A",
                "expected_yield": "N/A",
                "reasoning": "No valid markets found",
                "confidence": "low",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Sort by score and get top recommendation
        scored_markets.sort(key=lambda x: x['score'], reverse=True)
        best = scored_markets[0]
        
        # Build reasoning
        reasoning = (
            f"{best['symbol']} on {best['protocol']} offers {best['implied_apy']}% fixed APY "
            f"with ${best['liquidity_usd']:,.0f} liquidity. "
            f"Expires in {best['days_to_expiry']} days. "
            f"Strong combination of yield and safety."
        )
        
        # Determine confidence based on liquidity and APY
        confidence = "high" if best['liquidity_usd'] > 5_000_000 and best['implied_apy'] > 5 else "medium"
        
        return {
            "predicted_best_token": best['symbol'],
            "protocol": best['protocol'],
            "expected_yield": f"{best['implied_apy']}%",
            "underlying_yield": f"{best['underlying_apy']}%",
            "liquidity_usd": best['liquidity_usd'],
            "days_to_expiry": best['days_to_expiry'],
            "reasoning": reasoning,
            "confidence": confidence,
            "top_3_alternatives": [
                {
                    "symbol": m['symbol'],
                    "apy": f"{m['implied_apy']}%",
                    "protocol": m['protocol']
                }
                for m in scored_markets[1:4]
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in predict_best_yield: {e}")
        return {
            "predicted_best_token": "Error",
            "expected_yield": "N/A",
            "reasoning": f"Analysis failed: {str(e)}",
            "confidence": "none",
            "timestamp": datetime.utcnow().isoformat()
        }


def predict_future_yield(
    token: str,
    days: int = 3,
    current_apy: Optional[float] = None,
    historical_data: Optional[List[float]] = None
) -> List[Dict[str, Any]]:
    """
    Predict future yield for a given token over N days.
    
    Uses simple trend analysis if historical data is available,
    otherwise provides conservative estimates with confidence intervals.
    
    Args:
        token: Token symbol
        days: Number of days to predict
        current_apy: Current APY as decimal (e.g., 0.08 for 8%)
        historical_data: Optional list of historical APY values
        
    Returns:
        List of predictions with dates, APY estimates, and confidence intervals
    """
    if days < 1 or days > 365:
        logger.warning(f"Invalid prediction days: {days}. Using 7 days.")
        days = 7
    
    try:
        predictions = []
        
        # If we have current APY, use it as baseline
        if current_apy is not None:
            base_apy = current_apy * 100  # Convert to percentage
        else:
            # Default conservative estimate
            base_apy = 5.0
            logger.info(f"No current APY provided for {token}, using default {base_apy}%")
        
        # Calculate trend if historical data available
        trend = 0
        if historical_data and len(historical_data) >= 2:
            # Simple linear trend
            trend = (historical_data[-1] - historical_data[0]) / len(historical_data)
            trend = max(min(trend, 0.5), -0.5)  # Cap trend at ±0.5% per day
        
        # Generate predictions
        for day in range(1, days + 1):
            # Apply trend with diminishing effect
            predicted_apy = base_apy + (trend * day * 0.5)  # 50% trend dampening
            
            # Add small random variation (±0.3%)
            import random
            variation = random.uniform(-0.3, 0.3)
            predicted_apy += variation
            
            # Ensure APY stays positive and reasonable
            predicted_apy = max(0.1, min(predicted_apy, 50.0))
            
            # Calculate confidence interval (wider for further predictions)
            confidence_range = 0.5 + (day * 0.1)  # Increases with time
            
            prediction_date = datetime.utcnow() + timedelta(days=day)
            
            predictions.append({
                "day": day,
                "date": prediction_date.strftime("%Y-%m-%d"),
                "predicted_apy": round(predicted_apy, 2),
                "confidence_interval": {
                    "lower": round(predicted_apy - confidence_range, 2),
                    "upper": round(predicted_apy + confidence_range, 2)
                },
                "confidence": "high" if day <= 3 else "medium" if day <= 7 else "low"
            })
        
        logger.info(f"Generated {len(predictions)} yield predictions for {token}")
        return predictions
        
    except Exception as e:
        logger.error(f"Error in predict_future_yield: {e}")
        return [{
            "day": 1,
            "date": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "predicted_apy": 0,
            "error": str(e),
            "confidence": "none"
        }]


def analyze_market_risk(market: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze risk factors for a specific market.
    
    Args:
        market: Market data dictionary
        
    Returns:
        Risk analysis with score and factors
    """
    try:
        liquidity = market.get('liquidity', {}).get('usd', 0)
        implied_apy = market.get('impliedApy', 0) * 100
        volume = market.get('tradingVolume', {}).get('usd', 0)
        
        risk_factors = []
        risk_score = 0  # 0 = low risk, 10 = high risk
        
        # Liquidity risk
        if liquidity < 1_000_000:
            risk_factors.append("Low liquidity (< $1M)")
            risk_score += 3
        elif liquidity < 5_000_000:
            risk_factors.append("Moderate liquidity (< $5M)")
            risk_score += 1
        
        # APY risk (unusually high APY can indicate high risk)
        if implied_apy > 20:
            risk_factors.append("Very high APY (> 20%) - verify sustainability")
            risk_score += 2
        
        # Volume risk
        if volume < 100_000:
            risk_factors.append("Low trading volume")
            risk_score += 1
        
        # Determine overall risk level
        if risk_score <= 2:
            risk_level = "Low"
        elif risk_score <= 5:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors if risk_factors else ["No significant risks identified"],
            "recommendation": "Proceed with caution" if risk_score > 5 else "Suitable for most users"
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_market_risk: {e}")
        return {
            "risk_level": "Unknown",
            "risk_score": 0,
            "risk_factors": [f"Analysis error: {str(e)}"],
            "recommendation": "Unable to assess risk"
        }