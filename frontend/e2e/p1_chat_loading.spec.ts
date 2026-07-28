import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_BASE_URL || '';

test.describe('P1-7: IntelAI Chat Loading Issue Trace', () => {
  test('Should trace chat request path from UI to backend', async ({ page, request }) => {
    await page.goto(BASE_URL + '/dashboard');
    await page.waitForLoadState('domcontentloaded');
    
    // Find chat input or chat interface
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"], [data-testid="chat-input"], .chat-input');
    const chatExists = await chatInput.count() > 0;
    
    if (chatExists) {
      console.log('Chat interface found on dashboard');
      
      // Monitor network requests
      const apiRequests: string[] = [];
      page.on('request', request => {
        if (request.url().includes('/api') || request.url().includes('/chat')) {
          apiRequests.push(request.url());
          console.log(`API Request: ${request.method()} ${request.url()}`);
        }
      });
      
      page.on('response', response => {
        if (response.url().includes('/api') || response.url().includes('/chat')) {
          console.log(`API Response: ${response.status()} ${response.url()}`);
        }
      });
      
      // Try to send a simple test message
      await chatInput.first().fill('test message');
      
      // Look for send button
      const sendButton = page.locator('button[type="submit"], [data-testid="send-button"], .send-button, button:has-text("Send")');
      const sendExists = await sendButton.count() > 0;
      
      if (sendExists) {
        await sendButton.first().click();
        
        // Wait for potential response
        await page.waitForTimeout(3000);
        
        console.log('Chat requests made:', apiRequests);
        
        // Check if chat API was called
        const chatApiCalled = apiRequests.some(url => url.includes('/chat') || url.includes('/query') || url.includes('/ask'));
        
        if (chatApiCalled) {
          console.log('Chat API endpoint was called successfully');
        } else {
          console.warn('Chat API endpoint was not called - possible frontend routing issue');
        }
      } else {
        console.warn('Send button not found');
      }
    } else {
      console.warn('Chat interface not found on dashboard - checking other pages');
      
      // Check other pages that might have chat
      const pagesWithChat = ['/workspace', '/knowledge', '/admin'];
      
      for (const pagePath of pagesWithChat) {
        await page.goto(BASE_URL + pagePath);
        await page.waitForLoadState('domcontentloaded');
        
        const chatOnPage = await page.locator('input[type="text"], textarea, [contenteditable="true"], [data-testid="chat-input"], .chat-input').count() > 0;
        
        if (chatOnPage) {
          console.log(`Chat interface found on ${pagePath}`);
          break;
        }
      }
    }
  });

  test('Should test chat API endpoint directly', async ({ request }) => {
    // Test the chat API endpoint directly
    const chatEndpoints = [
      '/api/v1/chat',
      '/api/chat',
      '/chat',
      '/api/v1/query',
      '/api/query'
    ];
    
    for (const endpoint of chatEndpoints) {
      try {
        const response = await request.post(`${BASE_URL}${endpoint}`, {
          data: {
            query: 'test message',
            message: 'test message'
          }
        });
        
        console.log(`Chat endpoint ${endpoint}: ${response.status()}`);
        
        if (response.ok()) {
          const data = await response.json();
          console.log(`Chat endpoint ${endpoint} returned:`, data);
          expect(data).toBeDefined();
          break; // Found working endpoint
        }
      } catch (error) {
        console.log(`Chat endpoint ${endpoint} failed:`, error);
      }
    }
  });

  test('Should check chat loading performance and timing', async ({ page }) => {
    const navigationStart = Date.now();
    
    await page.goto(BASE_URL + '/dashboard');
    await page.waitForLoadState('domcontentloaded');
    
    const loadTime = Date.now() - navigationStart;
    console.log(`Dashboard load time: ${loadTime}ms`);
    
    // Check for chat-specific loading indicators
    const chatLoading = page.locator('[data-testid="chat-loading"], .chat-loading, .message-loading');
    const hasLoadingIndicator = await chatLoading.count() > 0;
    
    if (hasLoadingIndicator) {
      console.log('Chat loading indicator found');
      
      // Wait for loading to complete
      await page.waitForSelector('[data-testid="chat-loading"], .chat-loading, .message-loading', { state: 'hidden', timeout: 10000 }).catch(() => {
        console.warn('Chat loading indicator did not disappear within timeout');
      });
    }
    
    // Check for any chat-related error messages
    const chatErrors = page.locator('[data-testid="chat-error"], .chat-error, .message-error');
    const errorCount = await chatErrors.count();
    
    if (errorCount > 0) {
      const errorText = await chatErrors.first().textContent();
      console.error(`Chat error found: ${errorText}`);
    } else {
      console.log('No chat errors detected');
    }
  });

  test('Should trace WebSocket connections for real-time chat', async ({ page }) => {
    const wsConnections: string[] = [];
    
    page.on('websocket', ws => {
      console.log(`WebSocket connection: ${ws.url()}`);
      wsConnections.push(ws.url());
    });
    
    await page.goto(BASE_URL + '/dashboard');
    await page.waitForLoadState('domcontentloaded');
    
    // Wait a bit for any WebSocket connections
    await page.waitForTimeout(2000);
    
    if (wsConnections.length > 0) {
      console.log('WebSocket connections found:', wsConnections);
    } else {
      console.log('No WebSocket connections detected - chat may use HTTP polling');
    }
  });
});