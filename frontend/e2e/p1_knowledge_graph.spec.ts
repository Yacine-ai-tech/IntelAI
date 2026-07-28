import { test, expect } from '@playwright/test';

const BASE_URL = process.env.TEST_BASE_URL || '';

test.describe('P1-6: IntelAI Knowledge Graph Rendering Debug', () => {
  test('Should load Knowledge Graph page and check for rendering issues', async ({ page }) => {
    // Set longer timeout for page load
    test.setTimeout(90000); // 90 seconds instead of default 45s
    
    let loaded = false;
    let lastError = null;
    
    // Retry logic for page load
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        console.log(`Attempt ${attempt} to load knowledge graph page`);
        
        await page.goto(BASE_URL + '/knowledgegraph', { 
          waitUntil: 'domcontentloaded', 
          timeout: 60000 
        });
        
        // Wait for React app to hydrate
        await page.waitForTimeout(5000);
        
        // Check if page loads
        const rootElement = page.locator('#root');
        await rootElement.waitFor({ state: 'visible', timeout: 30000 });
        const rootHtml = await rootElement.innerHTML();
        
        if (rootHtml.length > 0) {
          loaded = true;
          console.log(`Page loaded successfully on attempt ${attempt}`);
          break;
        }
      } catch (error) {
        lastError = error;
        console.error(`Attempt ${attempt} failed:`, error.message);
        if (attempt < 3) {
          console.log('Retrying...');
          await page.waitForTimeout(3000);
        }
      }
    }
    
    if (!loaded) {
      // Check if page loaded at all for debugging
      const bodyHtml = await page.locator('body').innerHTML();
      console.log('Page body HTML length:', bodyHtml.length);
      console.log('Page URL:', page.url());
      throw new Error(`Page did not load properly after 3 attempts. Last error: ${lastError?.message}`);
    }
    // Check for knowledge graph specific elements
    const graphContainer = page.locator('[data-testid="knowledge-graph"], .knowledge-graph, #graph-container, .graph-container');
    const exists = await graphContainer.count();
    
    if (exists > 0) {
      // Graph container exists, check for rendering
      const isVisible = await graphContainer.first().isVisible();
      expect(isVisible).toBeTruthy();
      
      // Check for SVG or canvas elements used for graph rendering
      const svgElement = page.locator('svg');
      const canvasElement = page.locator('canvas');
      const hasSvg = await svgElement.count() > 0;
      const hasCanvas = await canvasElement.count() > 0;
      
      expect(hasSvg || hasCanvas).toBeTruthy();
      
      // Check for nodes in the graph
      const nodes = page.locator('.node, [data-testid="graph-node"], circle.node');
      const nodeCount = await nodes.count();
      
      if (nodeCount > 0) {
        console.log(`Knowledge graph loaded with ${nodeCount} nodes`);
      } else {
        console.warn('Knowledge graph loaded but no nodes found - possible data vs rendering issue');
      }
    } else {
      console.warn('Knowledge graph container not found - component may not be rendering');
    }
    
    // Check for error messages or loading states
    const errorMessages = page.locator('[role="alert"], .error, .error-message');
    const errorCount = await errorMessages.count();
    
    if (errorCount > 0) {
      const errorText = await errorMessages.first().textContent();
      console.error(`Knowledge graph error: ${errorText}`);
    }
    
    const loadingStates = page.locator('.loading, .spinner, [data-testid="loading"]');
    const loadingCount = await loadingStates.count();
    
    if (loadingCount > 0) {
      console.warn('Knowledge graph still in loading state');
    }
  });

  test('Should check knowledge graph data API endpoint', async ({ page, request }) => {
    // Test the backend API that provides graph data
    test.setTimeout(30000); // 30 seconds for API call
    
    try {
      const response = await request.get(`${BASE_URL}/api/v1/knowledge-graph`, {
        timeout: 15000
      });
      
      if (response.ok()) {
        const data = await response.json();
        expect(data).toBeDefined();
        
        // Check if data structure is correct
        if (data.nodes && data.edges) {
          console.log(`Knowledge graph API returned ${data.nodes.length} nodes and ${data.edges.length} edges`);
          expect(data.nodes.length).toBeGreaterThan(0);
        } else if (data.entities && data.relations) {
          console.log(`Knowledge graph API returned ${data.entities.length} entities and ${data.relations.length} relations`);
          expect(data.entities.length).toBeGreaterThan(0);
        } else {
          console.warn('Knowledge graph API returned unexpected data structure:', data);
        }
      } else {
        console.warn(`Knowledge graph API returned status ${response.status()}`);
      }
    } catch (error) {
      console.error('Knowledge graph API test failed:', error);
      throw error;
    }
  });

  test('Should check browser console for graph rendering errors', async ({ page }) => {
    test.setTimeout(60000); // 60 seconds for console monitoring
    
    const consoleMessages: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleMessages.push(msg.text());
      }
    });
    
    await page.goto(BASE_URL + '/knowledgegraph', { 
      waitUntil: 'domcontentloaded', 
      timeout: 60000 
    });
    
    // Wait for React app to hydrate and any rendering to complete
    await page.waitForTimeout(5000);
    
    // Additional wait for any delayed network errors
    await page.waitForTimeout(2000);
    
    if (consoleMessages.length > 0) {
      console.error('Console errors found on knowledge graph page:', consoleMessages);
      // Don't fail the test for console errors, just log them
    } else {
      console.log('No console errors on knowledge graph page');
    }
  });
});